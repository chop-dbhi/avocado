import cPickle as pickle
from hashlib import md5
from datetime import datetime
from functools import partial

from django.db import models, router
from django.db.models.sql import RawQuery
from django.core.paginator import EmptyPage, InvalidPage
from django.contrib.auth.models import User
from django.core.cache import cache as dcache

from forkit.models import ForkableModel

from avocado.conf import settings
from avocado.models import Field
from avocado.store.fields import JSONField
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS, trees
from avocado.fields import logictree
from avocado.columns.cache import cache as column_cache
from avocado.columns import utils, format
from avocado.utils.paginator import BufferedPaginator

__all__ = ('Scope', 'Perspective', 'Report', 'ObjectSet',
    'ObjectSetJoinThrough')

PAGE = 1
PAGINATE_BY = 10
CACHE_CHUNK_SIZE = 500
DEFAULT_COLUMNS = getattr(settings, 'COLUMNS', ())
DEFAULT_ORDERING = getattr(settings, 'COLUMN_ORDERING', ())

class Descriptor(ForkableModel):
    user = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    keywords = models.CharField(max_length=100, null=True)
    created = models.DateTimeField(default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)
    # explicitly denotes an instance for use in a session
    session = models.BooleanField(default=False)

    class Meta(object):
        abstract = True
        app_label = 'avocado'

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        super(Descriptor, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.name or self.pk)

    def get_reference_pk(self):
        if self.reference:
            return self.reference.pk

    def references(self, pk):
        "Returns the referenced object's ``pk`` is one exists."
        if self.reference:
            return self.reference.pk == int(pk)

    def diff(self, target=None, *args, **kwargs):
        if not target:
            target = self.reference
        if not target:
            return False
        return super(Descriptor, self).diff(target, *args, **kwargs)

    def has_changed(self):
        return bool(self.diff())


class Context(Descriptor):
    """A generic interface for storing an arbitrary context around the data
    model. The object defining the context must be serializable.
    """
    store = JSONField(null=True)
    timestamp = models.DateTimeField(editable=False, default=datetime.now)

    class Meta(object):
        abstract = True
        app_label = 'avocado'

    def _get_obj(self, obj=None):
        if obj is None:
            return self.store or {}
        return obj

    def _get_contents(self, obj):
        """A ``Context`` is driven by the abstraction layer of the ``Field``,
        ``Criterion`` and ``Column`` classes. Each ``obj`` will be empty or
        contain data (like primary keys) referring to objects of the former
        mentioned classes.

        Returns a list of ``Field`` primary keys.
        """
        pass

    def _parse_contents(self, obj, *args, **kwargs):
        """Encapsulates any processing that must be performed on ``obj`` and
        returns a function that takes a queryset and returns a queryset.
        """
        pass

    def cache_is_valid(self, timestamp=None):
        if timestamp and timestamp > self.timestamp:
            return True
        return False

    def is_valid(self, obj):
        """Takes an object and determines if the data structure is valid for
        this particular context.
        """
        if isinstance(obj, dict):
            return True
        return False

    def read(self):
        return self._get_obj()

    def write(self, obj=None, *args, **kwargs):
        obj = self._get_obj(obj)
        self.store = obj
        self.timestamp = datetime.now()

    def has_permission(self, obj=None, user=None):
        obj = self._get_obj(obj)

        field_ids = set([int(i) for i in self._get_contents(obj)])
        # if not requesting to see anything, early exit
        if not field_ids:
            return True

        fields = Field.objects.public(user)

        # filter down to requested fields
        ids = set(fields.values('id').filter(id__in=field_ids).values_list('id', flat=True))

        if len(ids) != len(field_ids) or not all([i in field_ids for i in ids]):
            return False

        return True

    def get_queryset(self, obj=None, queryset=None, using=DEFAULT_MODELTREE_ALIAS, *args, **kwargs):
        obj = self._get_obj(obj)

        if queryset is None:
            queryset = trees[using].get_queryset()

        func = self._parse_contents(obj, using=using, *args, **kwargs)
        queryset = func(queryset, *args, **kwargs)
        return queryset


class Scope(Context):
    "Stores information needed to provide scope to data."

    cnt = models.PositiveIntegerField('count', editable=False)
    # used for book keeping. if a reference exists, this implies this instance
    # has represents another context.
    reference = models.ForeignKey('self', null=True)


    def _get_contents(self, obj):
        self._node = logictree.transform(obj)
        return self._node.get_field_ids()

    def _parse_contents(self, obj, *args, **kwargs):
        self._node = logictree.transform(obj)
        return self._node.apply

    def is_valid(self, obj):
        if hasattr(self, '_node'):
            del self._node
        return super(Scope, self).is_valid(obj)

    def save(self, *args, **kwargs):
        self.cnt = self.get_queryset().distinct().count()
        super(Scope, self).save(*args, **kwargs)

    def get_text(self):
        node = logictree.transform(self._get_obj())
        return node.text


class Perspective(Context):
    # used for book keeping. if a reference exists, this implies this instance
    # has represents another context.
    reference = models.ForeignKey('self', null=True)

    def _get_obj(self, obj=None):
        obj = obj or {}
        if self.store is not None:
            copy = self.store.copy()
        else:
            copy = {}

        copy.update(obj)

        # supply default values
        if not copy.has_key('columns'):
            copy['columns'] = list(DEFAULT_COLUMNS)
        if not copy.has_key('ordering'):
            copy['ordering'] = list(DEFAULT_ORDERING)

        copy['columns'] = [int(x) for x in copy['columns']]
        copy['ordering'] = [(int(x), y) for x, y in copy['ordering']]

        # ordering of a column cannot exist when the column is not present
        for i, (x, y) in enumerate(iter(copy['ordering'])):
            if x not in copy['columns']:
                copy['ordering'].pop(i)

        return copy

    def _get_contents(self, obj):
        ids = obj['columns'] + [x for x,y in obj['ordering']]

        # saves a query
        if not ids:
            return ids

        # get all field ids associated with requested columns
        return Field.objects.filter(column__id__in=set(ids)).values_list('id',
            flat=True)

    def _parse_contents(self, obj, *args, **kwargs):
        def func(queryset, columns=[], ordering=[], *args, **kwargs):
            queryset = utils.add_columns(queryset, columns, *args, **kwargs)
            queryset = utils.add_ordering(queryset, ordering, *args, **kwargs)
            return queryset

        return partial(func, columns=obj['columns'], ordering=obj['ordering'])

    def header(self):
        store = self.read()
        header = []

        for x in store['columns']:
            c = column_cache.get(x)
            if c is None:
                continue
            o = {'id': x, 'name': c.name, 'direction': ''}
            for y, z in store['ordering']:
                if x == y:
                    o['direction'] = z
                    break
            header.append(o)

        return header

    def get_columns_as_fields(self):
        store = self.read()
        header = []

        for x in store['columns']:
            c = column_cache.get(x)
            cfields = c.conceptfields.select_related('field').order_by('order')
            if len(cfields) == 1:
                header.append(c.name)
            else:
                header.extend([x.name or x.field.name for x in cfields])
        return header

    def format(self, iterable, format_type):
        store = self.read()
        rules = utils.column_format_rules(store['columns'], format_type)
        return format.library.format(iterable, rules, format_type)


class Report(Descriptor):
    "Represents a combination ``scope`` and ``perspective``."
    REPORT_CACHE_KEY = 'reportcache'

    scope = models.OneToOneField(Scope)
    perspective = models.OneToOneField(Perspective)
    # used for book keeping. if a reference exists, this implies this instance
    # has represents another context.
    reference = models.ForeignKey('self', null=True)

    def _center_cache_offset(self, count, offset, buf_size=CACHE_CHUNK_SIZE):
        """The ``offset`` will be relative to the next requested row. To ensure
        a true 'sliding window' of data, the offset must be adjusted to be::

            offset - (buf_size / 2)

        The edge cases will be relative to the min (0) and max number of rows
        that exist.
        """
        mid = int(buf_size / 2.0)

        # lower bound
        if (offset - mid) < 0:
            offset = 0
        # upper bound
        elif (offset + mid) > count:
            offset = count - buf_size
        # in the middle
        else:
            offset = offset - mid

        return offset

    def _set_queryset_offset_limit(self, queryset, offset, limit):
        lower = offset
        upper = offset + limit
        return queryset[lower:upper]

    def _execute_raw_query(self, queryset):
        """Take a ``QuerySet`` object and executes it. No customization or
        processing of the query should take place here.
        """
        using = router.db_for_read(queryset.model)
        sql, params = queryset.query.get_compiler(using).as_sql()
        raw = RawQuery(sql, using, params)
        raw._execute_query()
        return raw.cursor.fetchall()

    def paginator_and_page(self, cache, buf_size=CACHE_CHUNK_SIZE):
        paginator = BufferedPaginator(count=cache['count'], offset=cache['offset'],
            buf_size=buf_size, per_page=cache['per_page'])

        try:
            page = paginator.page(cache['page_num'])
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)

        return paginator, page

    def get_datakey(self, request):
        return md5(request.session._session_key + 'data').hexdigest()

    def cache_is_valid(self, timestamp=None):
        if self.scope.cache_is_valid(timestamp) and \
            self.perspective.cache_is_valid(timestamp):
            return True
        return False

    # in it's current implementation, this will try to get the requested
    # page from cache, or re-execute the query and store off the new cache
    def get_page_from_cache(self, cache, buf_size=CACHE_CHUNK_SIZE):
        paginator, page = self.paginator_and_page(cache, buf_size)

        # now we can fetch the data
        if page.in_cache():
            data = dcache.get(cache['datakey'])
            if data is not None:
                return page.get_list(pickle.loads(data))

    def refresh_cache(self, cache, queryset, adjust_offset=True, buf_size=CACHE_CHUNK_SIZE):
        """Does not utilize existing cache if it exists. This is an implied
        cache invalidation mechanism.
        """
        paginator, page = self.paginator_and_page(cache, buf_size)

        queryset = self._set_queryset_offset_limit(queryset, cache['offset'], buf_size)

        # since the page is not in cache new data must be requested, therefore
        # the offset should be re-centered relative to the page offset
        if adjust_offset:
            cache['offset'] = self._center_cache_offset(cache['count'], page.offset(), buf_size)

        data = self._execute_raw_query(queryset)
        dcache.set(cache['datakey'], pickle.dumps(data))

        paginator.offset = cache['offset']
        paginator.object_list = data

        try:
            page = paginator.page(cache['page_num'])
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)

        assert page.in_cache()

        return page.get_list()

    def update_cache(self, cache, queryset, buf_size=CACHE_CHUNK_SIZE):
        """Tries to use cache if it exists, this implies that the cache is still
        valid and a page that is not in cache has been requested.
        """
        paginator, page = self.paginator_and_page(cache, buf_size)

        # since the page is not in cache new data must be requested, therefore
        # the offset should be re-centered relative to the page offset
        cache['offset'] = self._center_cache_offset(cache['count'], page.offset(), buf_size)

        # determine any overlap between what we have with ``cached_rows`` and
        # what the ``page`` requires.
        has_overlap, start_term, end_term = paginator.get_overlap(cache['offset'])

        # we can run a partial query and use some of the existing rows for our
        # updated cache
        if has_overlap is False:
            queryset = self._set_queryset_offset_limit(queryset, *start_term)
            data = self._execute_raw_query(queryset)
        else:
            rdata = dcache.get(cache['datakey'])
            if rdata is None:
                return self.refresh_cache(cache, queryset, adjust_offset=False,
                    buf_size=buf_size)

            data = pickle.loads(rdata)
            # check to see if there is partial data to be prepended
            if start_term[0] is not None:
                tmp = self._set_queryset_offset_limit(queryset, *start_term)
                partial_data = self._execute_raw_query(tmp)
                data = partial_data + data[:-start_term[1]]

            # check to see if there is partial data to be appended
            if end_term[0] is not None:
                tmp = self._set_queryset_offset_limit(queryset, *end_term)
                partial_data = self._execute_raw_query(tmp)
                data = data[end_term[1]:] + partial_data

        dcache.set(cache['datakey'], pickle.dumps(data))

        paginator.offset = cache['offset']
        paginator.object_list = data

        page = paginator.page(cache['page_num'])
        assert page.in_cache()

        return page.get_list()

    def _get_count(self, queryset):
        tmp = queryset.all()
        tmp.query.clear_ordering(True)
        return tmp.count()

    def get_queryset(self, timestamp=None, using=DEFAULT_MODELTREE_ALIAS, **context):
        """Returns a ``QuerySet`` object that is generated from the ``scope``
        and ``perspective`` objects bound to this report. This should not be
        used directly when requesting data since it does not utlize the cache
        layer.
        """
        unique = count = None
        queryset = trees[using].get_queryset().values('id').distinct()

        # first argument is ``None`` since we want to use the session objects
        queryset = self.scope.get_queryset(None, queryset, using=using, **context)
        unique = self._get_count(queryset)

        queryset = self.perspective.get_queryset(None, queryset, using=using)
        count = self._get_count(queryset)

        return queryset, unique, count

    def has_permission(self, user):
        # ensure the requesting user has permission to view the contents of
        # both the ``scope`` and ``perspective`` objects
        # TODO add per-user caching for report objects
        if self.scope.has_permission(user=user) and self.perspective.has_permission(user=user):
            return True
        return False


class ObjectSet(Descriptor):
    """
    Provides a means of saving off a set of objects.

    `criteria' is persisted so the original can be rebuilt. `removed_ids'
    is persisted to know which objects have been excluded explicitly from the
    set. This could be useful when testing for if there are new objects
    available when additional data has been loaded, while still excluding
    the removed objects.

    `ObjectSet' must be subclassed to add the many-to-many relationship
    to the "object" of interest.
    """
    scope = models.OneToOneField(Scope, editable=False)
    cnt = models.PositiveIntegerField('count', default=0, editable=False)

    class Meta(object):
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.now()
        self.modified = datetime.now()
        super(ObjectSet, self).save(*args, **kwargs)


class ObjectSetJoinThrough(models.Model):
    """
    Adds additional information about the objects that have been ``added`` and
    ``removed`` from the original set.

    For instance, additional objects that are added which do not match the
    conditions currently associated with the ``ObjectSet`` should be flagged
    as ``added``. If in the future they match the conditions, the flag can be
    removed.

    Any objects that are removed from the set should be marked as ``removed``
    even if they were added at one time. This is too keep track of the objects
    that have been explicitly removed from the set.
    """
    removed = models.BooleanField(default=False)
    added = models.BooleanField(default=False)

    class Meta(object):
        abstract = True

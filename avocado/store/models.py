try:
    import cPickle as pickle
except ImportError:
    import pickle
from hashlib import md5
from datetime import datetime
from functools import partial

from django.db import models, transaction, connections, DEFAULT_DB_ALIAS
from django.db.models.sql import RawQuery
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, InvalidPage
from django.contrib.auth.models import User
from django.core.cache import cache as mcache

from avocado.conf import settings
from avocado.models import Field
from avocado.db_fields import PickledObjectField
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS, trees
from avocado.fields import logictree
from avocado.columns.cache import cache as column_cache
from avocado.columns import utils, format
from avocado.utils.paginator import BufferedPaginator

__all__ = ('Scope', 'Perspective', 'Report')

PAGE = 1
PAGINATE_BY = 10
CACHE_CHUNK_SIZE = 500
DEFAULT_COLUMNS = getattr(settings, 'COLUMNS', ())
DEFAULT_ORDERING = getattr(settings, 'COLUMN_ORDERING', ())

class Descriptor(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'avocado'

    def __unicode__(self):
        return u'%s' % self.name


class Context(Descriptor):
    """A generic interface for storing an arbitrary context around the data
    model. The object defining the context must be serializable.
    """
    store = PickledObjectField(default={})
    definition = models.TextField(editable=False, null=True)
    timestamp = models.DateTimeField(editable=False, default=datetime.now())

    class Meta:
        abstract = True
        app_label = 'avocado'

    def define(self):
        "Interprets the stored data structure."
        raise NotImplementedError

    def _get_obj(self, obj=None):
        if obj is None:
            obj = self.store or {}
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

    def is_valid(self, obj):
        """Takes an object and determines if the data structure is valid for
        this particular context.
        """
        if isinstance(obj, dict):
            return True
        return False

    def read(self):
        return self._get_obj(self.store or {})

    def write(self, obj, *args, **kwargs):
        obj = self._get_obj(obj)
        print obj
        self.store = obj
        self.timestamp = datetime.now()

    def has_permission(self, obj=None, user=None):
        obj = self._get_obj(obj)

        field_ids = set([int(i) for i in self._get_contents(obj)])
        # if not requesting to see anything, early exit
        if not field_ids:
            return True

        if user and settings.FIELD_GROUP_PERMISSIONS:
            groups = user.groups.all()
            fields = Field.objects.restrict_by_group(groups)
        else:
            fields = Field.objects.public()

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

    def _get_contents(self, obj):
        return logictree.transform(obj).get_field_ids()

    def _parse_contents(self, obj, *args, **kwargs):
        node = logictree.transform(obj, *args, **kwargs)
        return node.apply


class Perspective(Context):
    def _get_obj(self, obj=None):
        obj = super(Perspective, self)._get_obj(obj)
        if not obj.has_key('columns'):
            obj['columns'] = list(DEFAULT_COLUMNS)
        if not obj.has_key('ordering'):
            obj['ordering'] = list(DEFAULT_ORDERING)
        return obj

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

    def header_row(self):
        store = self.read()
        header = []

        for x in store['columns']:
            c = column_cache.get(x)
            for y, z in store['ordering']:
                if x == y:
                    header.append((c.name, z))
                    break
            else:
                header.append((c.name, ''))
        return header

    def format(self, iterable, format_type):
        store = self.read()

        rules = utils.column_format_rules(store['columns'], format_type)
        return format.library.format(iterable, rules, format_type)


class Report(Descriptor):
    "Represents a combination ``scope`` and ``perspective``."
    REPORT_CACHE_KEY = 'reportcache'

    scope = models.ForeignKey(Scope)
    perspective = models.ForeignKey(Perspective)

    def _cache_is_valid(self, timestamp=None):
        if timestamp:
            if timestamp > self.scope.timestamp and \
                timestamp > self.perspective.timestamp:
                return True
        return False

    def _center_cache_offset(self, count, offset, buf_size=CACHE_CHUNK_SIZE):
        """The ``offset`` will be relative to the next requested row. To ensure
        a true 'sliding window' of data, the offset must be adjusted to be::

            offset - (buf_size / 2)

        The edge cases will be relative to the min (0) and max number of rows
        that exist.
        """
        mid = int(buf_size / 2)

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
        sql, params = queryset.query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
        raw = RawQuery(sql, DEFAULT_DB_ALIAS, params)
        raw._execute_query()
        return raw.cursor.fetchall()

    # in it's current implementation, this will try to get the requested
    # page from cache, or re-execute the query and store off the new cache
    def _get_page_from_cache(self, cache, buf_size=CACHE_CHUNK_SIZE):
        """Attempts
        The cache datastructure:

            cache = {
                'count': 10000,
                'unique': 2000,
                'offset': 100,
                'datakey': some_md5_hash,
                'timestamp': datetime object,
            }
        """
        count = cache['count']
        offset = cache['offset']
        datakey = cache['datakey']
        per_page = cache['per_page']
        page_num = cache['page_num']

        # create a theoretical paginator representing the rows stored off.
        # since it is still unknown whether the cache contains the requested
        # data, the data is not yet fetched so to reduce the overhead
        paginator = BufferedPaginator(count=count, offset=offset,
            buf_size=buf_size, per_page=per_page)

        # get the requested page. note, this is relative to the ``count``
        try:
            page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)

        # now we can fetch the data
        if page.in_cache():
            data = mcache.get(datakey, None)
            print '_get_page', data is not None
            if data is not None:
                return page.get_list(pickle.loads(data))

    def _update_cache(self, cache, queryset, buf_size=CACHE_CHUNK_SIZE):
        count = cache['count']
        offset = cache['offset']
        per_page = cache['per_page']
        page_num = cache['page_num']

        paginator = BufferedPaginator(count=count, offset=offset,
            buf_size=buf_size, per_page=per_page)

        try:
            page = paginator.page(page_num)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)

        # since the page is not in cache new data must be requested, therefore
        # the offset should be re-centered relative to the page offset
        offset = self._center_cache_offset(count, page.offset(), buf_size)

        # only test for overlap is there is existing data
        if cache.has_key('datakey'):
            # determine any overlap between what we have with ``cached_rows`` and
            # what the ``page`` requires.
            has_overlap, start_term, end_term = paginator.get_overlap(offset)

            print has_overlap, start_term, end_term

            # we can run a partial query and use some of the existing rows for our
            # updated cache
            if has_overlap is False:
                queryset = self._set_queryset_offset_limit(queryset, *start_term)
                rows = self._execute_raw_query(queryset)
            else:
                data = mcache.get(cache['datakey'], None)
                if data is None:
                    raise RuntimeError
                rows = pickle.loads(data)
                # check to see if there is partial data to be prepended
                if start_term[0] is not None:
                    tmp = self._set_queryset_offset_limit(queryset, *start_term)
                    partial_rows = self._execute_raw_query(tmp)
                    rows = partial_rows + rows[:-start_term[1]]

                # check to see if there is partial data to be appended
                if end_term[0] is not None:
                    tmp = self._set_queryset_offset_limit(queryset, *end_term)
                    partial_rows = self._execute_raw_query(tmp)
                    rows = rows[end_term[1]:] + partial_rows
        else:
            queryset = self._set_queryset_offset_limit(queryset, offset, buf_size)
            rows = self._execute_raw_query(queryset)

        # update paginator to reflect new ``offset`` and ``rows``
        paginator.offset = offset
        paginator.object_list = rows

        page = paginator.page(page_num)
        assert page.in_cache()

        cache['offset'] = offset

        return rows, page.get_list()

    def get_queryset(self, run_counts=False, using=DEFAULT_MODELTREE_ALIAS, **context):
        """Returns a ``QuerySet`` object that is generated from the ``scope``
        and ``perspective`` objects bound to this report. This should not be
        used directly when requesting data since it does not utlize the cache
        layer.
        """
        unique = count = None
        queryset = trees[using].get_queryset()

        # first argument is ``None`` since we want to use the session objects
        queryset = self.scope.get_queryset(None, queryset, using=using, **context)
        if run_counts:
            unique = queryset.values('id').count()

        queryset = self.perspective.get_queryset(None, queryset, using=using)
        if run_counts:
            count = queryset.count()

        return queryset, unique, count

    def resolve(self, request, format_type, page_num=None, per_page=None, using=DEFAULT_MODELTREE_ALIAS):
        """Generates a report based on the ``scope`` and ``perspective``
        objects associated with this object.

        There are a few methods of trying to create the report::

            - *fetch from the session cache* - this is firstly dependent on the
            ``scope`` and ``perspective`` objects, such that the cache
            timestamps must be at a later time than the objects last write. if
            this is determined to be true, the session cache is deemed valid.
            the secondary piece is to determine if the requested data exists in
            cache. this is dependent on the ``page`` and ``per_page`` values.

            - *fetch from the global cache* (not implemented) - this is
            dependent on the unique combination of ``scope`` and ``perspective``
            requirements. if a hash is found representing this combination,
            then the data is fetched. the second step is to determine if the
            requested data exists in cache. this is dependent on the ``page``
            and ``per_page`` values.

            - *generate a new query* -

        """
        user = request.user
        request.session.modified = True
        # ensure the requesting user has permission to view the contents of
        # both the ``scope`` and ``perspective`` objects
        # TODO add per-user caching for report objects
        if not self.scope.has_permission(user=user) or \
            not self.perspective.has_permission(user=user):
            raise PermissionDenied

        # define the default context for use by ``get_queryset``
        # TODO can this be defined elsewhere? only scope depends on this, but
        # the user object has to propagate down from the view
        context = {'user': user}

        # fetch the report cache from the session, default to a new dict with
        # a few defaults. if a new dict is used, this implies that this a
        # report has not been resolved yet this session.
        cache = request.session.get(self.REPORT_CACHE_KEY, {
            'offset': 0,
            'page_num': 1,
            'per_page': 10,
            'timestamp': None,
        })

        # only update the cache if there are values specified for either arg
        if page_num:
            cache['page_num'] = int(page_num)
        if per_page:
            cache['per_page'] = int(per_page)

        # test if the cache is still valid, then attempt to fetch the requested
        # page from cache
        if self._cache_is_valid(cache['timestamp']):
            rows = self._get_page_from_cache(cache)

            # ``rows`` will only be None if no cache was found
            if rows is not None:
                return list(self.perspective.format(rows, format_type))

            # since the cache is not invalid, the counts do not have to be run
            queryset, unique, count = self.get_queryset(run_counts=False, **context)

        else:
            queryset, unique, count = self.get_queryset(run_counts=True, **context)
            cache.update({
                'unique': unique,
                'count': count,
            })

        # this timestamp must be set right after the queryset was generated
        # since it relies on other objects
        cache['timestamp'] = datetime.now()

        data, rows = self._update_cache(cache, queryset)

        if not cache.has_key('datakey'):
            cache['datakey'] = md5(request.session._session_key + 'data').hexdigest()

        key = cache['datakey']
        mcache.set(key, pickle.dumps(data), None)

        request.session[self.REPORT_CACHE_KEY] = cache

        return list(self.perspective.format(rows, format_type))


class ObjectSet(Descriptor):
    """Provides a means of saving off a set of objects.

    `criteria' is persisted so the original can be rebuilt. `removed_ids'
    is persisted to know which objects have been excluded explicitly from the
    set. This could be useful when testing for if there are new objects
    available when additional data has been loaded, while still excluding
    the removed objects.

    `ObjectSet' must be subclassed to add the many-to-many relationship
    to the "object" of interest.
    """
    scope = models.ForeignKey(Scope)
    cnt = models.PositiveIntegerField('count', editable=False)

    class Meta:
        abstract = True

    def bulk_insert(self, object_ids, join_table, fk1, fk2):
        "Uses the SQL COPY command to populate the M2M join table."
        from cStringIO import StringIO

        cursor = connections['default'].cursor()

        buff = StringIO()

        for oid in object_ids:
            buff.write('%s\t%s\n' % (self.id, oid))
        buff.seek(0)

        cursor.copy_from(buff, join_table, columns=(fk1, fk2))

        transaction.set_dirty()
        transaction.commit_unless_managed()

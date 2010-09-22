try:
    import cPickle as pickle
except ImportError:
    import pickle
from datetime import datetime
from functools import partial

from django.db import models, transaction, connections, DEFAULT_DB_ALIAS
from django.core.exceptions import PermissionDenied
from django.db.models.sql import RawQuery
from django.contrib.auth.models import User

from avocado.conf import settings
from avocado.models import Field, Column
from avocado.db_fields import PickledObjectField
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS, trees
from avocado.fields import logictree
from avocado.columns import utils, format
from avocado.utils.paginator import BufferedPaginator

__all__ = ('Scope', 'Perspective', 'Report')

PAGE = 1
PAGINATE_BY = 10
CACHE_CHUNK_SIZE = 500

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
    timestamp = models.DateTimeField(editable=False)

    class Meta:
        abstract = True
        app_label = 'avocado'

    def define(self):
        "Interprets the stored data structure."
        raise NotImplementedError

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
        return self.store

    def write(self, obj, *args, **kwargs):
        self.store = obj
        self.timestamp = datetime.now()

    def has_permission(self, obj=None, user=None):
        obj = obj or self.store or {}

        field_ids = set(self._get_contents(obj))
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
        obj = obj or self.store or {}

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
    def _get_contents(self, obj):
        ids = []
        columns = obj.get('columns', None)
        ordering = obj.get('ordering', None)

        if columns:
            ids += columns
        if ordering:
            ids += [x for x,y in ordering]

        # saves a query
        if not ids:
            return ids

        # get all field ids associated with requested columns
        return Field.objects.filter(column__id__in=set(ids)).values_list('id',
            flat=True)

    def _parse_contents(self, obj, *args, **kwargs):
        columns = obj.get('columns', None)
        ordering = obj.get('ordering', None)

        def func(queryset, columns=[], ordering=[], *args, **kwargs):
            queryset = utils.add_columns(queryset, columns, *args, **kwargs)
            queryset = utils.add_ordering(queryset, ordering, *args, **kwargs)
            return queryset

        return partial(func, columns=columns, ordering=ordering)

    def format(self, obj, iterable, format_type):
        columns = obj.get('column', None)
        if columns:
            rules = utils.column_format_rules(columns, format_type)
            return format.library.format(iterable, rules, format_type)
        return iterable


class Report(Descriptor):
    "Represents a combination ``scope`` and ``perspective``."
    REPORT_CACHE_KEY = 'reportcache'

    scope = models.ForeignKey(Scope)
    perspective = models.ForeignKey(Perspective)

    def _center_cache_offset(count, offset, buf_size=CACHE_CHUNK_SIZE):
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
    def _get_from_cache(self, request, page_num, per_page, buf_size=CACHE_CHUNK_SIZE,
        using=DEFAULT_MODELTREE_ALIAS):

        """
        The cache datastructure:

            cache = {
                'count': 10000,
                'unique': 2000,
                'offset': 100,
                'rows': (...),
                'timestamps': {...},
            }
        """
        user = request.user
        cache = request.session.get(self.REPORT_CACHE_KEY, {})
        timestamps = cache.get('timestamps', {})

        queryset, unique, count = self._get_queryset(timestamps, user, using=using)

        # implies cache is invalid
        if count is not None:
            # reset to first page, since the number of rows may have changed
            offset = 0
            rows = []
        # cache is still valid, so let's try to use it
        else:
            unique = cache['unique']
            count = cache['count']
            offset = cache['offset']
            rows = pickle.loads(cache['rows'])

        # create a paginator of the current ``rows`` which is relative to
        # ``offset``. 
        paginator = BufferedPaginator(count=count, offset=offset,
            buf_size=buf_size, object_list=rows, per_page=per_page)

        # get the requested page. note, this is relative to the ``count``
        page = paginator.page(page_num)

        if page.in_cache():
            return page.get_list()

        # since the page is not in cache new data must be requested, therefore
        # the offset should be re-centered relative to the page offset
        offset = self._center_cache_offset(count, page.offset, buf_size)

        # determine any overlap between what we have with ``cached_rows`` and
        # what the ``page`` requires.
        has_overlap, start_term, end_term = paginator.get_overlap(offset)

        # we can run a partial query and use some of the existing rows for our
        # updated cache
        if has_overlap is False:
            queryset = queryset[start_term[0]:start_term[1]]
            rows = self._execute_query(queryset)
        else:
            # check to see if there is partial data to be prepended
            if start_term[0] is not None:
                partial_rows = self._execute_query(queryset[start_term[0]:start_term[1]])
                rows = partial_rows + rows[:-start_term[1]]
            if end_term[0] is not None:
                partial_rows = self._execute_query(queryset[end_term[0]:end_term[1]])
                rows = rows[end_term[1]:] + partial_rows

        cache = {
            'unique': unique,
            'count': count,
            'offset': offset,
            'rows': pickle.dumps(rows),
        }

        request.session[self.REPORT_CACHE_KEY] = cache
        request.session.modified = True

        # update paginator to reflect new ``offset`` and ``rows``
        paginator.offset = offset
        paginator.object_list = rows

        page = paginator.page(page_num)

        assert page.in_cache()
        return page.get_list()


    def _get_queryset(self, timestamps, user=None, using=DEFAULT_MODELTREE_ALIAS):
        """Returns a ``QuerySet`` object that is generated from the ``scope``
        and ``perspective`` objects bound to this report. This should not be
        used directly when requesting data since it does not utlize the cache
        layer.
        """
        unique = count = None

        if timestamps:
            scope_cached = self.scope.cached(timestamps['scope'])
            perspective_cached = self.perspective.cached(timestamps['perspective'])
        else:
            scope_cached = False
            perspective_cached = False

        queryset = trees[using].get_queryset()

        # TODO the flexibility of defining this ``context`` is lacking, since
        # it is hardcoded here, but the need for additional kwargs is unknown
        # to me at the moment. if eventually needed, it may be necessary to
        # make this a setting that then dynamically is generated.
        context = {'user': user}

        # if the ``scope`` is not cached, the unique count must be re-run
        # this is not dependent on the ``perspective``
        queryset = self.scope.get_queryset(queryset, user=user,
            use_cache=scope_cached, using=using, context=context)

        if not scope_cached:
            unique = queryset.values('id').count()

        queryset = self.perspective.get_queryset(queryset, user=user,
            use_cache=perspective_cached, using=using)

        if not scope_cached or not perspective_cached:
            count = queryset.count()

        return queryset, unique, count

    def resolve(self, request, format_type, page, per_page, using=DEFAULT_MODELTREE_ALIAS):
        rows = self._get_from_cache(request, page, per_page, using=using)
        return self._format_rows(rows, format_type)


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

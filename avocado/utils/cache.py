import time

from django.core.paginator import EmptyPage, InvalidPage
from django.utils import simplejson
from django.db import transaction, DEFAULT_DB_ALIAS
from django.db.models.sql.query import RawQuery

from avocado.settings import settings
from avocado.models import CriterionConcept, ColumnConcept
from avocado.criteria.utils import CriterionSet
from avocado.columns.utils import ColumnSet, get_columns, get_column_orders
# from avocado.columns.format import get_formatters
from avocado.utils.paginator import BufferedPaginator

DEFAULT_COLUMNS = settings.DEFAULT_COLUMNS
DEFAULT_COLUMN_ORDERING = settings.DEFAULT_COLUMN_ORDERING

class QuerySessionCache(object):
    """Stores query results for a given session.
    
        `criterion_concepts' - defines the CriterionConcept queryset which
        will be used to fetch and process user-defined conditions.
        
        `column_concepts' - defines the ColumnConcept queryset which will
        be used to fetch and process user-defined columns from for
        reporting purposes.
        
        `column_ids' - a list of column ids to fetch from `column_ids' to
        report
        
        `column_ordering' - a list of pairs specifying a column id and the
        direction e.g. [(1, 'asc'), (5, 'desc')]
        
        `criteria_tree' - a tree structure containing the necessary logic
        for defining query conditions
        
        `limit' - the number of rows to be stored in the session
        
        `page' - the "page" number of results which is relative to
        `paginate_by'
        
        `paginate_by' - the number of results per page
    """

    def __init__(self, criterion_concepts, column_concepts, criteria_tree,
        column_ids=DEFAULT_COLUMNS, column_ordering=DEFAULT_COLUMN_ORDERING,
        limit=100, page=1, paginate_by=10):

        self.criterion_concepts = criterion_concepts
        self.column_concepts = column_concepts
        self.criteria_tree = criteria_tree
        self.column_ids = column_ids
        self.column_ordering = column_ordering
        self.limit = limit
        self.page = page
        self.paginate_by = paginate_by
        self.counter = 0
        
        self._set = None
        self._extra_attrs = set([])
        
    def __getitem__(self, key):
        return getattr(self, key, None)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def __setattr__(self, key, value):
        if not hasattr(self, key) and hasattr(self, '_extra_attrs'):
            self._extra_attrs.add(key)
        object.__setattr__(self, key, value)

    def __getstate__(self):
        "Provides picklable interface that does not evaluate querysets."
        dict_ = self.__dict__.copy()

        criterion_concepts = dict_.pop('criterion_concepts')
        column_concepts = dict_.pop('column_concepts')

        dict_['criterion_query'] = criterion_concepts.query
        dict_['column_query'] = column_concepts.query

        return dict_

    def __setstate__(self, dict_):
        criterion_concepts = CriterionConcept.objects.all()
        column_concepts = ColumnConcept.objects.all()

        criterion_concepts.query = dict_.pop('criterion_query')
        column_concepts.query = dict_.pop('column_query')

        dict_['criterion_concepts'] = criterion_concepts
        dict_['column_concepts'] = column_concepts

        self.__dict__.update(dict_)

    def _get_set(self):
        return self._set
    
    def _set_set(self, set_):
        "Handles the logic for setting an ObjectSet."
        # for a temporary ObjectSet, "renew" ObjectSet only if the cached
        # ObjectSet is not a temporary one
        if set_.id is None:
            if self._set is None or self._set.id is not None:
                self._set = set_
                self.clear()
        else:
            if self._set is not None:
                # overwrite temporary set or different saved set
                if self._set.id is None or self._set.id != set_.id:
                    self._set = set_
                    self.clear()
            else:
                self._set = set_

    set_obj = property(_get_set, _set_set)

    def clear(self):
        for key in self._extra_attrs:
            delattr(self, key)
        self._extra_attrs = set([])

    def update(self, dict_):
        for k, v in dict_.items():
            setattr(self, k, v)


class QuerySessionCacheManager(object):
    def __init__(self, queryset, cache, modeltree, pre_criteria=None,
        column_ids=None, column_ordering=None, page=None, paginate_by=None,
        removed_ids=None, logged_query=None):

        self.queryset = queryset
        self.cache = cache
        self.modeltree = modeltree
        self.column_ids = column_ids
        self.column_ordering = column_ordering
        self.page = page and int(page) or None
        self.paginate_by = paginate_by and int(paginate_by) or None
        self.removed_ids = removed_ids
        self.logged_query = logged_query
        self.column_set = ColumnSet(cache['column_concepts'], modeltree) 
        self.criterion_set = CriterionSet(cache['criterion_concepts'], modeltree)
        self._cache = self._copy_cache(cache)
        self._exec_count = False
        self._new_columns = False
        self._new_ordering = False

    def _copy_cache(self, cache):
        dict_ = {}
        for key, value in cache.__dict__.items():
            if not key.startswith('_') and key not in ('column_concepts',
                'criterion_concepts'):
                dict_[key] = value
        return dict_

    def _init_queryset(self, can_use_cache=True):
        """Determine the initial `queryset'. Two scenarios can occur here:
        
            `query' acts as the gatekeeper for whether the cache can be used.
            if `query' is None, the cached `pre_criteria' has changed.
            
            [2010-04-14] When a `set_id' is present, applying of conditions is
            ignored.
            
        At this step, the `unique_count' must be set before any `columns' are
        added.
        """
        queryset = self.queryset.all()

        if self.cache['query'] is None or not can_use_cache:
            can_use_cache = False
            self._exec_count = True
            if not self.cache['set_obj'] or self.cache['set_obj'].id is None:
                queryset = self._add_wheres(queryset)
            self._cache['unique_count'] = queryset.distinct().count()
        else:
            queryset.query = self.cache['query']

        return queryset, can_use_cache

    def _add_wheres(self, queryset):
        if self._cache.get('pre_criteria', None):
            pre_criteria = self._cache['pre_criteria']

            t0 = time.time()
            queryset = self.criterion_set.add_filters(queryset,
                pre_criteria)
            tt = time.time() - t0
            ta = tt / (len(pre_criteria) or 1)

            if self.logged_query is not None:
                self.logged_query.criteria = simplejson.dumps(pre_criteria)
                self.logged_query.criteria_exec = tt
                self.logged_query.criteria_avg = ta
            
            # this will only apply when this is a temporary set.
            if self._cache.get('removed_ids', None):
                queryset = queryset.exclude(id__in=self._cache['removed_ids'])

        return queryset

    @transaction.commit_on_success
    def _remove_from_set(self, queryset, can_use_cache=True):
        """Removes objects from the current patient set. If the patient
        set is saved, this operation incurs an additional database hit.
        """
        if self.removed_ids is not None:
            # update unique count
            unique_count = self._cache['unique_count'] - len(self.removed_ids)
            self.cache['set_obj'].count = unique_count
            
            # if this is a saved PatientSet, hit database and make change
            if self.cache['set_obj'].id is not None:
                # TODO refactor to remove dependency on attribute 'patients'
                self.cache['set_obj'].patients.remove(*self.removed_ids)
                
                if self.cache['set_obj'].removed_ids:
                    _removed_ids = [int(x) for x in self.cache['set_obj'].removed_ids.split(',')]
                else:
                    _removed_ids = []
                removed_ids = set(_removed_ids + self.removed_ids)

                self.cache['set_obj'].removed_ids = ','.join([str(x) for x in removed_ids])
                self.cache['set_obj'].save()
                self._cache['removed_ids'] = []

                queryset = self.cache['set_obj'].patients.all()                
            else:
                removed_ids = self._cache.get('removed_ids', []) + self.removed_ids
                queryset = queryset.exclude(id__in=removed_ids)
                # update cache diff for consecutive requests
                self._cache['removed_ids'] = removed_ids

            self._cache['unique_count'] = unique_count
            self._exec_count = True
            can_use_cache = False

        return queryset, can_use_cache

    def _set_columns(self, queryset, can_use_cache=True):
        """Implements the logic necessary for determining which columns need to
        be applied to the queryset.

        There are two scenarios:
            - the `can_use_cache' flag is False in which case, regardless if
            `column_ids' is fetched from cache, the cache is refreshed.
            NOTE: this will always be the case when the first query of a
            user session is being run

            - a new set of `column_ids' is available, in which case the
            cache needs to be reset

        The queryset and a boolean is returned to propagate for further
        processing.
        """
        if self.column_ids is not None:
            column_ids = self.column_ids

            if column_ids != self._cache.get('column_ids', []):
                self._cache['column_ids'] = column_ids 
                self._exec_count = True
                can_use_cache = False
        else:
            column_ids = self._cache['column_ids']

        if not can_use_cache:
            self._new_columns = True

            columns, ignored = get_columns(self.cache['column_concepts'],
                column_ids)

            t0 = time.time()
            queryset = self.column_set.add_columns(queryset, columns)
            tt = time.time() - t0
            ta = tt / (len(column_ids) or 1)

            if self.logged_query is not None:
                self.logged_query.columns_exec = tt
                self.logged_query.columns_avg = ta

            self._cache['columns'] = columns

        return queryset, can_use_cache

    def _set_ordering(self, queryset, can_use_cache=True):
        """Implements the logic necessary for determining the column ordering
        to be applied to the queryset

        There are two scenarios:
            - the `can_use_cache' flag is False in which case, regardless if
            `column_ordering' is fetched from cache, the cache is refreshed.
            NOTE: this will always be the case when the first query of a
            user session is being run

            - a new set of `column_ordering' is available, in which case the
            cache needs to be reset

        The queryset and a boolean is returned to propagate for further
        processing.
        """
        if self.column_ordering is not None:
            column_ordering = self.column_ordering

            if column_ordering != self._cache.get('column_ordering', []):
                self._cache['column_ordering'] = column_ordering
                can_use_cache = False
                self._new_ordering = True
        else:
            column_ordering = self._cache['column_ordering']

        if not can_use_cache:
            column_orders, ignored = get_column_orders(self.cache['column_concepts'],
                column_ordering)

            t0 = time.time()
            queryset = self.column_set.add_ordering(queryset,
                column_orders)
            tt = time.time() - t0
            ta = tt / (len(column_ordering) or 1)

            if self.logged_query is not None:
                self.logged_query.ordering_exec = tt
                self.logged_query.ordering_avg = ta

            self._cache['column_orders'] = column_orders

        return queryset, can_use_cache

    def _set_formatters(self, columns, column_orders):
        pc, pf, rc, rf = get_formatters(columns, column_orders)

        self._cache['pretty_columns'] = pc
        self._cache['pretty_formatters'] = pf
        self._cache['raw_columns'] = rc
        self._cache['raw_formatters'] = rf

    def _update_formatters(self, column_orders):
        """"The `pretty_columns' only need to be updated regarding order and
        direction.
        """
        for dict_ in self._cache['pretty_columns']:
            order = column_orders.get(dict_['_concept'], None)
            if order is not None:
                dict_.update(order)
            else:
                dict_['direction'] = ''
                dict_['order'] = None

    def _page_in_cache(self, can_use_cache=True):
        """Determines if a new slice of data has been requested by
        processing the `page' and `paginate_by' by values. If this is
        different from the cache, then it must be determined if the
        slice of data exists in the cache.
        """
        new_page = False
        if self.page is not None:
            if self.page != self._cache['page']:
                self._cache['page'] = self.page
                new_page = True
        else:
            self.page = self._cache['page']

        if self.paginate_by is not None:
            if self.paginate_by != self._cache['paginate_by']:
                self._cache['paginate_by'] = self.paginate_by
                new_page = True
        else:
            self.paginate_by = self._cache['paginate_by']

        # up to this point, if `can_use_cache' is True, nothing about the query has
        # changed. if `new_page' is True, a new slice of data is being requested
        # and this code block tests whether the slice exists in the cache
        if can_use_cache and new_page:
            # only check the cache if the number of rows exceeds the cached limit
            if self._cache['count'] > self._cache['limit']:
                paginator = BufferedPaginator(self._cache['count'], self._cache['offset'],
                    self._cache['limit'], self._cache['rows'], self.paginate_by)
                try:
                    page_obj = paginator.page(self.page)
                except (EmptyPage, InvalidPage):
                    page_obj = paginator.page(paginator.num_pages)

                if not page_obj.in_cache():
                    can_use_cache = False

                del paginator, page_obj
                
        return can_use_cache

    def _add_slice(self, queryset, count):
        """Determines the OFFSET and LIMIT params for the query.
        By default a large chunk of data retrieved in anticipation of
        paginating.
        """
        limit = self._cache['limit']

        if count <= limit:
            offset = 0
            end = limit
        else:
            mid = (self.page - 1) * self.paginate_by
            half_size = int(limit / 2)
            offset = mid - half_size
            end = offset + limit

            if offset < 0:
                offset = 0
                end = limit
            elif end > count:
                end = count
                offset = end - limit

        self._cache['offset'] = offset
        return queryset[offset:end]

    def _setup_query(self):
        """Run through the flags that determine which aspects of the query need
        to be modified.
        """
        queryset, can_use_cache = self._init_queryset()
        queryset, can_use_cache = self._remove_from_set(queryset, can_use_cache)

        queryset, can_use_cache = self._set_columns(queryset, can_use_cache)
        queryset, can_use_cache = self._set_ordering(queryset, can_use_cache)        

        # rebuild the formatters cache if the columns have changed.
        # this has been established after the columns ave been setup,
        # therefore if the columns were not updated, but the ordering
        # has changed, the formatters display info has to be updated
        if self._new_columns:
            self._set_formatters(self._cache['columns'],
                self._cache['column_orders'])
        elif self._new_ordering:
            self._update_formatters(self._cache['column_orders'])

        # determine if this page is NOT in the cache (follows)
        can_use_cache = self._page_in_cache(can_use_cache)

        if not can_use_cache:
            self._execute_query(queryset)

        # this must always be called to ensure no errors have occurred which
        # could corrupt the cache.
        self.cache.update(self._cache) 
        del self._cache
        
        return self.cache
        
    def _count(self, queryset):
        queryset = queryset.all()
        # remove ordering for better performance
        queryset.query.clear_ordering()
        return queryset.count()

    def _execute_query(self, queryset):
        # cache query object prior to slicing
        self._cache['query'] = queryset.query
        if self._exec_count:
            self._cache['count'] = self._count(queryset)

        queryset = self._add_slice(queryset, self._cache['count'])
        
        sql, params = queryset.query.get_compiler(DEFAULT_DB_ALIAS).as_sql()
        raw_query = RawQuery(sql, DEFAULT_DB_ALIAS, params)

        t0 = time.time()
        raw_query._execute_query()
        tt = time.time() - t0

        cursor = raw_query.cursor

        # update post-query specific data elements
        self._cache['rows'] = cursor.fetchall()
        self._cache['sql'] = hasattr(cursor, 'query') and cursor.query or \
            cursor.cursor.query
        self._cache['counter'] = self._cache['counter'] + 1

        if self.logged_query is not None:
            self.logged_query.sql_exec = tt
            self.logged_query.sql = self._cache['sql']
            self.logged_query.counter = self._cache['counter']
            self.logged_query.count = self._cache['count']
            self.logged_query.save()

    def _get_paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = BufferedPaginator(self.cache['count'],
                self.cache['offset'], self.cache['limit'], self.cache['rows'],
                self.paginate_by)
        return self._paginator
    paginator = property(_get_paginator)
    
    def _get_page_obj(self):
        if not hasattr(self, '_page_obj'):
            try:
                self._page_obj = self.paginator.page(self.page)
            except (EmptyPage, InvalidPage):
                self._page_obj = self.paginator.page(self.paginator.num_pages)
        return self._page_obj
    page_obj = property(_get_page_obj)

    def update_cache(self):
        return self._setup_query()

    def add_initial_patients(self):
        """Takes a PatientSet instance and associates patients currently
        defined in cache and updates cache to reflect change.
        """
        queryset, can_use_cache = self._init_queryset()  

        ids = queryset.values_list('id', flat=True)
        self.cache['set_obj'].bulk_patient_insert(ids)

        transaction.set_dirty()
        transaction.commit_unless_managed()
        
        return self.cache
        
        

from copy import deepcopy
from django.db.models import Q, Count, Sum, Avg, Max, Min, StdDev, Variance
from django.db.models.query import REPR_OUTPUT_SIZE, QuerySet
from django.db.models.sql.constants import LOOKUP_SEP
from modeltree.utils import M, resolve_lookup

class Aggregator(object):
    def __init__(self, field_name, model):
        self.field_name = field_name
        self.model = model
        self.aggregates = {}
        self.where = []
        self.having = []
        self.groupby = []
        self.orderby = []

    def __deepcopy__(self):
        return self._clone()

    def __len__(self):
        return len(self._construct())

    def __repr__(self):
        queryset = self._construct()
        if not isinstance(queryset, QuerySet):
            return str(queryset)
        data = list(self[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = '...(remaining elements results)...'
        return repr(data)

    def __getitem__(self, key):
        return self._result_iter(self._construct().__getitem__(key))

    def __iter__(self):
        return self._result_iter(self._construct())

    def _result_iter(self, queryset):
        agg = self.aggregates.keys()[0]
        for obj in queryset.iterator():
            keys = []
            for key in self.groupby:
                keys.append(obj[key])
            if len(keys) == 1:
                yield {keys[0]: obj[agg]}
            else:
                yield {tuple(keys): obj[agg]}

    def _construct(self):
        queryset = self.model.objects.all()
        # If no group by clause is defined, this is a full table aggregation
        if self.groupby:
            queryset = queryset.values(*self.groupby)
        if self.where:
            queryset = queryset.filter(*self.where)
        if self.aggregates:
            if self.groupby:
                queryset = queryset.annotate(**self.aggregates)
            else:
                queryset = queryset.aggregate(**self.aggregates)
        if self.having:
            queryset = queryset.filter(*self.having)
        if self.orderby:
            queryset = queryset.order_by(*self.orderby)
        if not self.groupby:
            return dict(queryset)
        return queryset

    def _clone(self):
        clone = self.__class__(self.field_name, self.model)
        clone.aggregates = deepcopy(self.aggregates)
        clone.where = deepcopy(self.where)
        clone.having = deepcopy(self.having)
        clone.groupby = deepcopy(self.groupby)
        clone.orderby = deepcopy(self.orderby)
        return clone

    def _aggregate(self, *groupby, **aggregates):
        clone = self._clone()
        clone.aggregates.update(aggregates)
        clone.groupby = [resolve_lookup(x, tree=clone.model) for x in groupby]
        return clone

    def filter(self, *values, **filters):
        clone = self._clone()
        # One or more values allowed values for the applied to this
        # data field. This is currently restricted to an `exact` or `in`
        # operator.
        if values:
            if len(values) == 1:
                condition = clone.field_name, values[0]
            else:
                condition = '{0}__in'.format(clone.field_name), values
            clone.where.append(M(tree=clone.model, **dict([condition])))

        # Separate out the conditions that apply to aggregations. The
        # non-aggregation conditions will always be applied before the
        # aggregation is applied.
        for key, value in filters.iteritems():
            if key.split(LOOKUP_SEP)[0] in clone.aggregates:
                condition = Q(**dict([(key, value)]))
                clone.having.append(condition)
            else:
                condition = M(tree=clone.model, **dict([(key, value)]))
                clone.where.append(condition)
        return clone

    def exclude(self, *values, **filters):
        clone = self._clone()
        # One or more values allowed values for the applied to this
        # data field. This is currently restricted to an `exact` or `in`
        # operator.
        if values:
            if len(values) == 1:
                condition = clone.field_name, values[0]
            else:
                condition = '{0}__in'.format(clone.field_name), values
            clone.where.append(~M(tree=clone.model, **dict([condition])))

        # Separate out the conditions that apply to aggregations. The
        # non-aggregation conditions will always be applied before the
        # aggregation is applied.
        for key, value in filters.iteritems():
            if key.split(LOOKUP_SEP)[0] in clone.aggregates:
                condition = ~Q(**dict([(key, value)]))
                clone.having.append(condition)
            else:
                condition = ~M(tree=clone.model, **dict([(key, value)]))
                clone.where.append(condition)
        return clone

    def order_by(self, *fields):
        clone = self._clone()
        orderby = []
        for f in fields:
            direction = ''
            if f.startswith('-'):
                f = f[1:]
                direction = '-'
            if f not in self.aggregates:
                f = resolve_lookup(f, tree=clone.model)
            orderby.append(direction + f)
        clone.orderby = orderby
        return clone

    def count(self, *groupby):
        "Performs a COUNT aggregation."
        aggregates = {'count': Count(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def sum(self, *groupby):
        "Performs an SUM aggregation."
        aggregates = {'sum': Sum(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def avg(self, *groupby):
        "Performs an AVG aggregation."
        aggregates = {'avg': Avg(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def min(self, *groupby):
        "Performs an MIN aggregation."
        aggregates = {'min': Min(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def max(self, *groupby):
        "Performs an MAX aggregation."
        aggregates = {'max': Max(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def stddev(self, *groupby):
        "Performs an STDDEV aggregation."
        aggregates = {'stddev': StdDev(self.field_name)}
        return self._aggregate(*groupby, **aggregates)

    def variance(self, *groupby):
        "Performs an VARIANCE aggregation."
        aggregates = {'variance': Variance(self.field_name)}
        return self._aggregate(*groupby, **aggregates)


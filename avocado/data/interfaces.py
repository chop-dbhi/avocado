from django.db import models
from django.core import exceptions
from django.utils.encoding import smart_unicode
from avocado.core import utils, loader
from avocado.conf import settings
from avocado.stats.agg import Aggregator


registry = loader.Registry()


# Utility functions to loading interfaces classes

def get_interfaces():
    classes = []
    for path in settings.FIELD_INTERFACES:
        classes.append(utils.import_by_path(path))
    return classes

def get_base_interface():
    return utils.import_by_path(settings.BASE_FIELD_INTERFACE)

def get_interface(field):
    # Check if the field or model instances themselves have a method for
    # contributing a field interface
    if hasattr(field, 'contribute_field_interface'):
        return field.contribute_field_interface()
    elif hasattr(field.model, 'contribute_field_interface'):
        return field.model.contribute_field_interface()

    # Fallback to available interfaces, then the default
    for klass in get_interfaces():
        if klass.valid_for_field(field):
            return klass
    return get_base_interface()


class FieldInterface(object):
    # Denotes whether this interface supports _real_ coded values. The API
    # is defined below to support it, however there is no guarantee the field
    # itself supports it.
    supports_coded_values = False

    @classmethod
    def valid_for_field(cls, field):
        "Checks if this interface is valid for field."
        return True

    def __init__(self, instance):
        self._instance = instance

    def __unicode__(self):
        if self._instance.name:
            return self._instance.name
        return u'{0} {1}'.format(self.model._meta.verbose_name,
            self.field.verbose_name).title()


    # Fields

    @property
    def _value_field(self):
        "The field to be used when performing lookups for the underlying data."
        return self.field

    @property
    def _label_field(self):
        "The field that represents the label for field."
        return self.field

    @property
    def _code_field(self):
        "The field that represents the coded value for field."
        return self.field

    @property
    def _order_field(self):
        "The field to be used when ordering the underlying data."
        return self.field

    @property
    def _search_field(self):
        "The field used for performing string-based searches."
        return self._label_field


    # QuerySets

    def _base_queryset(self, order=True, **context):
        """Returns a QuerySet for field or None if model is not defined.

        Downstream implementations may pass additional `context` keyword
        arguments such as `user` or `request`.

        Overridding/extending this method will propagate throughout other
        methods and properties utilizing a QuerySet of the field's data.
        """
        queryset = self.model._default_manager.all()
        if order:
            queryset = queryset.order_by(self._order_field.name)
        return queryset

    def _values_queryset(self, distinct=True, **context):
        "Returns a ValuesListQuerySet of values."
        queryset = self._base_queryset(**context)\
            .values_list(self._value_field.name, flat=True)
        if distinct:
            queryset = queryset.distinct()
        return queryset

    def _labels_queryset(self, distinct=True, **context):
        "Returns a ValuesListQuerySet of labels."
        queryset = self._base_queryset(**context)\
            .values_list(self._label_field.name, flat=True)
        if distinct:
            queryset = queryset.distinct()
        return queryset

    def _codes_queryset(self, distinct=True, **context):
        "Returns a ValuesListQuerySet of codes."
        queryset = self._base_queryset(**context)\
            .values_list(self._code_field.name, flat=True)
        if distinct:
            queryset = queryset.distinct()
        return queryset


    # Public

    @property
    def model(self):
        "Returns the model class `field` represents."
        return self._instance.model

    @property
    def field(self):
        "Returns the model field `field` represents."
        return self._instance.field

    @property
    def internal_type(self):
        "Returns the internal type of field."
        return utils.get_internal_type(self._value_field)

    @property
    def simple_type(self):
        "Returns a simple type mapped from the internal type."
        return utils.get_simple_type(self._value_field)

    @property
    def nullable(self):
        """Returns whether field is nullable.

        This affects downstream query construction and validation since
        querying for null values when they are not allowed will never return
        results.
        """
        return self._instance.field.null

    def value_exists(self, value, **context):
        "Optimized method for checking if a value exists."
        lookup = {self._value_field.name: value}
        return self._values_queryset(**context).filter(**lookup).exists()

    def values_exist(self, values, **context):
        "Optimized method for checking if all values exists."
        # This seems unecessary, but is typically faster than performing
        # any kind of distinct count.. and checking against the length.
        # TODO some benchmarking may be in order..
        return all(self.value_exists(v) for v in values)

    def label_for_value(self, value, **context):
        "Returns a label for `value`."
        # No difference, don't waste a lookup
        if self._label_field is self._value_field:
            return smart_unicode(value)

        # Note, multiple objects will not be returned since this is a
        # distinct query
        try:
            lookup = {self._value_field.name: value}
            return self._labels_queryset(**context).get(**lookup)
        except exceptions.ObjectDoesNotExist:
            pass

    def code_for_value(self, value, **context):
        "Returns a code for `value`."
        # No difference, don't waste a lookup or field has choices
        if self._code_field is self._value_field:
            return value

        # Note, multiple objects will not be returned since this is a
        # distinct query
        try:
            lookup = {self._value_field.name: value}
            return self._codes_queryset(**context).get(**lookup)
        except exceptions.ObjectDoesNotExist:
            pass

    def labels_for_values(self, values, **context):
        "Returns labels for multiple values."
        # Map against single value labeler
        if self._label_field is self._value_field:
            return tuple(self.label_for_value(v) for v in values)

        lookup = {'{0}__in'.format(self._value_field.name): values}

        # Order does not matter since values are being mapped after
        mapping = dict(self._base_queryset(order=False, **context).filter(**lookup)\
            .values_list(self._value_field.name, self._label_field.name))
        return tuple(mapping[v] for v in values if v in mapping)

    def codes_for_values(self, values, **context):
        "Returns codes for multiple values."
        # Map against single value coder
        if self._code_field is self._value_field:
            return tuple(self.code_for_value(v) for v in values)

        lookup = {'{0}__in'.format(self._value_field.name): values}

        # Order does not matter since values are being mapped after
        mapping = dict(self._base_queryset(order=False, **context).filter(**lookup)\
            .values_list(self._value_field.name, self._code_field.name))
        return tuple(mapping[v] for v in values if v in mapping)


    def values(self, **context):
        "Returns a distinct list of the values."
        return self._values_queryset(**context)

    def labels(self, **context):
        "Returns an distinct list of labels corresponding to the values."
        return self._labels_queryset(**context)

    def codes(self, **context):
        "Returns a distinct set of coded values for this field"
        return self._codes_queryset(**context)

    def choices(self, **context):
        "Returns a distinct set of labeled values."
        return self._base_queryset(**context)\
            .values_list(self._value_field.name, self._label_field.name)\
            .distinct()

    def coded_choices(self, **context):
        "Returns a distinct set of labeled codes."
        return self._base_queryset(**context)\
            .values_list(self._code_field.name, self._label_field.name)\
            .distinct()

    def search(self, query, match='contains', **context):
        "Rudimentary search for string-based values."
        # Check type of search field..
        if utils.get_simple_type(self._search_field) != 'string':
            return
        if match not in ('contains', 'exact', 'regex'):
            raise ValueError("Match must be 'contains', 'exact', or 'regex'")
        queryset = self._base_queryset(**context)
        if not query:
            return queryset.empty()

        # Notice the `i` for case-insensitivity..
        lookup = u'{0}__i{1}'.format(self._search_field.name, match)

        return queryset.filter(**{lookup: query})\
            .values_list(self._value_field.name, self._search_field.name)\
            .distinct()


    # Data Aggregation Properties

    def _aggregator(self, **context):
        queryset = self._base_queryset(**context)
        return Aggregator(self._value_field, queryset=queryset)

    def size(self, **context):
        "Returns the count of distinct values."
        # Ensure this is distinct
        context['distinct'] = True
        return self._values_queryset(**context).count()

    def max(self, **context):
        "Returns the maximum value."
        return self._aggregator(**context).max()['max']

    def min(self, **context):
        "Returns the minimum value."
        return self._aggregator(**context).min()['min']

    def avg(self, **context):
        "Returns the average value. Only applies to quantitative data."
        if self.simple_type != 'number':
            return
        return self._aggregator(**context).avg()['avg']

    def sum(self, **context):
        "Returns the sum of values. Only applies to quantitative data."
        if self.simple_type != 'number':
            return
        return self._aggregator(**context).sum()['sum']

    def stddev(self, **context):
        "Returns the standard deviation. Only applies to quantitative data."
        if self.simple_type != 'number':
            return
        return self._aggregator(**context).stddev()['stddev']

    def variance(self, **context):
        "Returns the variance. Only applies to quantitative data."
        if self.simple_type != 'number':
            return
        return self._aggregator(**context).variance()['variance']

    def count(self, distinct=False, **context):
        "Returns an the aggregated counts."
        key = 'distinct_count' if distinct else 'count'
        return self._aggregator(**context).count(distinct=distinct)[key]


class ForeignKeyInterface(get_base_interface()):
    @classmethod
    def valid_for_field(cls, field):
        if isinstance(field, models.ForeignKey):
            return True

    def _base_queryset(self, **context):
        "Overridden to account for the `limit_choices_to` property."
        queryset = super(ForeignKeyInterface, self)._base_queryset(**context)
        return queryset.complex_filter(self.field.rel.limit_choices_to)


loader.autodiscover('interfaces')

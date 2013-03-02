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


    # Field choices

    def _has_field_choices(self):
        return bool(self._value_field._choices)

    @property
    def _field_choices(self):
        """Fields can have a hard-coded set of choices.

        This will used first where appropriate to reduce database lookups.
        """
        return self._value_field._choices

    @property
    def _field_choice_values(self):
        "Returns the values of the field choices."
        return zip(*self._field_choices)[0]

    @property
    def _field_choice_labels(self):
        "Returns the labels of the field choices."
        return zip(*self._field_choices)[1]


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
        if self._has_field_choices():
            return self._field_choice_values

        queryset = self._base_queryset(**context)\
            .values_list(self._value_field.name, flat=True)
        if distinct:
            queryset = queryset.distinct()
        return queryset

    def _labels_queryset(self, distinct=True, **context):
        "Returns a ValuesListQuerySet of labels."
        if self._has_field_choices():
            return self._field_choice_labels

        queryset = self._base_queryset(**context)\
            .values_list(self._label_field.name, flat=True)
        if distinct:
            queryset = queryset.distinct()
        return queryset

    def _codes_queryset(self, distinct=True, **context):
        "Returns a ValuesListQuerySet of codes."
        # Since codes are not in the field choices, make sure the code field
        # is the same field, otherwise use the default behavior
        if self._has_field_choices() and self._code_field is self._value_field:
            return self._field_choice_values

        queryset = self._base_queryset(**context)\
            .values_list(self._code_field.name, flat=True)
        if distinct:
            queryset = queryset.distinct()
        return queryset


    # Labelers and coders for single values

    def _label_for_value(self, value, **context):
        "Returns a label for `value`."
        # Fields with pre-defined choices take precedence
        if self._has_field_choices():
            return dict(self._field_choices).get(value)

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

    def _code_for_value(self, value, **context):
        "Returns a code for `value`."
        # Fields with pre-defined choices take precedence
        if self._has_field_choices() and self._code_field is self._value_field:
            return dict(self._field_choices).get(value)

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


    # Labelers and coders for multiple values

    def _labels_for_values(self, values, **context):
        # Map against single value labeler
        if self._has_field_choices() or self._label_field is self._value_field:
            return tuple(map(self._code_for_value, values))

        lookup = {'{0}__in'.format(self._value_field.name): values}

        # Order does not matter since values are being mapped after
        mapping = dict(self._base_queryset(order=False, **context).filter(**lookup)\
            .values_list(self._value_field.name, self._label_field.name))
        return tuple([mapping.get(v) for v in values])

    def _codes_for_values(self, values, **context):
        # Map against single value coder
        if self._has_field_choices() or self._code_field is self._value_field:
            return tuple(map(self._label_for_value, values))

        lookup = {'{0}__in'.format(self._value_field.name): values}

        # Order does not matter since values are being mapped after
        mapping = dict(self._base_queryset(order=False, **context).filter(**lookup)\
            .values_list(self._value_field.name, self._code_field.name))
        return tuple([mapping.get(v) for v in values])


    # Utilities

    def _value_exists(self, value, **context):
        "Optimized method for checking if a value exists."
        if self._has_field_choices():
            return value in dict(self._field_choices)
        lookup = {self._value_field.name: value}
        return self._values_queryset(**context).filter(**lookup).exists()


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

    def values(self, iterator=False, **context):
        "Returns a distinct list of the values."
        queryset = self._values_queryset(**context)
        if iterator:
            return iter(queryset)
        return tuple(queryset)

    def labels(self, iterator=False, **context):
        "Returns an distinct list of labels corresponding to the values."
        queryset = self._labels_queryset(**context)
        if iterator:
            return iter(queryset)
        return tuple(queryset)

    def codes(self, iterator=False, **context):
        "Returns a distinct set of coded values for this field"
        queryset = self._codes_queryset(**context)
        if iterator:
            return iter(queryset)
        return tuple(queryset)

    def choices(self, iterator=False, distinct=True, **context):
        "Returns a distinct set of labeled values."
        if self._has_field_choices():
            choices = self._field_choices
        else:
            choices = self._base_queryset(**context)\
                .values_list(self._value_field.name, self._label_field.name)
            if distinct:
                choices = choices.distinct()
        if iterator:
            return iter(choices)
        return tuple(choices)

    def coded_choices(self, iterator=False, distinct=True, **context):
        "Returns a distinct set of labeled codes."
        if self._has_field_choices() and self._code_field is self._value_field:
            choices = self._field_choices
        else:
            choices = self._base_queryset(**context)\
                .values_list(self._code_field.name, self._label_field.name)
            if distinct:
                choices = choices.distinct()
        if iterator:
            return iter(choices)
        return tuple(choices)

    def search(self, query, match='contains', iterator=False, distinct=True, **context):
        "Rudimentary search for string-based values."
        # Check type of search field..
        if utils.get_simple_type(self._search_field) != 'string':
            return
        if not query:
            results = []
        elif match not in ('contains', 'exact', 'regex'):
            raise ValueError("Match must be 'contains', 'exact', or 'regex'.")
        else:
            # Notice the `i` for case-insensitivity..
            lookup = u'{0}__i{1}'.format(self._search_field.name, match)
            # Return tuple of the value and the label
            results = self._base_queryset(**context).filter(**{lookup: query})\
                .values_list(self._value_field.name, self._search_field.name)
            if distinct:
                results = results.distinct()
        if iterator:
            return iter(results)
        return tuple(results)


    # Data Aggregation Properties

    def _aggregator(self, **context):
        queryset = self._base_queryset(**context)
        return Aggregator(self._value_field, queryset=queryset)

    def size(self, **context):
        "Returns the count of distinct values."
        if self._has_field_choices():
            return len(self._value_field.choices)
        return self._values_queryset(**context).count()

    def max(self, **context):
        "Returns the maximum value."
        if self._has_field_choices():
            return max(self._field_choice_values)
        return self._aggregator(**context).max()['max']

    def min(self, **context):
        "Returns the minimum value."
        if self._has_field_choices():
            return min(self._field_choice_values)
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

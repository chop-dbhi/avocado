from django import forms
from django.db import models
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from modeltree.tree import trees
from avocado.core import loader
from avocado.conf import settings
from avocado.core.utils import get_form_class
from .operators import registry as operators


OPERATORS = settings.OPERATORS
INTERNAL_DATATYPE_FORMFIELDS = settings.INTERNAL_DATATYPE_FORMFIELDS


class Translator(object):
    """Given a `DataField` instance, a raw value and operator, a
    translator validates, cleans and constructs Django compatible
    lookups contained in the `query_modifiers` key in the output.

    The query modifiers are used to modify a `QuerySet` to filter
    the set down based on the raw input condition.
    """

    # An override of the list of supported operators for this particular
    # translator. This may be necessary for client programs which have
    # custom representations for certain fields.
    operators = None

    # Override of the field's default formfield class to be
    # used for validation. This is usually never necessary to override
    form_class = None

    def _parse_value(self, obj, key):
        """Handles parsing a value. This can be either a dict with a
        `value` and `label` key, some non-string iterable or the value
        itself.
        """
        if isinstance(obj, dict):
            return obj[key]
        if hasattr(obj, '__iter__'):
            return map(lambda x: self._parse_value(x, key), obj)
        return obj

    def _get_value(self, obj):
        return self._parse_value(obj, 'value')

    def _get_label(self, obj):
        return self._parse_value(obj, 'label')

    def get_operators(self, field):
        # Determine list of allowed operators
        return self.operators or OPERATORS[field.simple_type]

    def _validate_operator(self, field, uid, **kwargs):
        # Determine list of allowed operators
        allowed_operators = self.get_operators(field)

        # Special case for fields that are nullable
        if field.field.null:
            allowed_operators += ('isnull', '-isnull')

        # If uid is None, the default operator will be used
        uid = uid or allowed_operators[0]

        # Attempt to retrieve the operator.
        operator = operators.get(uid)

        # No operator is registered
        if operator is None:
            raise ValidationError(u'"{0}" is not a valid operator'.format(uid))

        # Ensure the operator is allowed
        if operator.uid not in allowed_operators:
            raise ValidationError(u'Operator "{0}" cannot be used for '
                                  'this translator'.format(operator))

        return operator

    def _validate_value(self, field, value, **kwargs):
        # If a form class is not specified, check to see if there is a custom
        # form_class specified for this datatype or if this translator has
        # one defined
        if 'form_class' not in kwargs:
            if self.form_class:
                kwargs['form_class'] = self.form_class
            elif field.internal_type in INTERNAL_DATATYPE_FORMFIELDS:
                name = INTERNAL_DATATYPE_FORMFIELDS[field.internal_type]
                kwargs['form_class'] = get_form_class(name)
            elif field.simple_type in INTERNAL_DATATYPE_FORMFIELDS:
                name = INTERNAL_DATATYPE_FORMFIELDS[field.simple_type]
                kwargs['form_class'] = get_form_class(name)

        # The formfield is being used to clean the value, thus no
        # 'required' validation errors should be raised.
        kwargs['required'] = False

        # Special handling for primary keys
        if isinstance(field.field, models.AutoField):
            kwargs.pop('form_class', None)
            queryset = field.objects
            if hasattr(value, '__iter__'):
                formfield = forms.ModelMultipleChoiceField(queryset, **kwargs)
            else:
                formfield = forms.ModelChoiceField(queryset, **kwargs)
            cleaned_value = formfield.clean(value)
            return cleaned_value

        # If this field is flagged as enumerable, use a select multiple
        # by default.
        if field.enumerable and 'widget' not in kwargs:
            kwargs['widget'] = forms.SelectMultiple(choices=field.choices())

        # The model field instance has a convenience method called `formfield`
        # that is suited for the field type
        formfield = field.field.formfield(**kwargs)

        # Special case for ``None`` values since all form fields seem to handle
        # the conversion differently. Simply ignore the cleaning if ``None``,
        # this scenario occurs when a list of values are being queried and one
        # of them is to lookup NULL values. Note, the None is handled
        # downstream and is contained with the query directly.
        if hasattr(value, '__iter__'):
            cleaned_value = []
            for x in value:
                if x is not None:
                    cleaned_value.append(formfield.clean(x))
                # Django assumes an empty string when given a ``NoneType``
                # for char-based form fields, this is to ensure ``NoneType``
                # are passed through unmodified
                else:
                    cleaned_value.append(None)
            return cleaned_value
        return formfield.clean(value)

    def _get_not_null_pk(self, field, tree):
        """The below logic is required to get the expected results back
        when querying for NULL values. Performing a LEFT OUTER JOIN will
        cause non-existent rows on the right-hand side to be 'filled' in
        with NULL values. If the condition is explicitly querying for NULL
        values, this condition ensures this row actually exists.

        Django assumes in all cases when querying on a NULL value all joins
        in the chain up to that point must be promoted to LEFT OUTER JOINs,
        which could be a reasonable assumption for some cases, but for
        getting the existent rows of data back for our purposes, the
        assumption is wrong.
        """

        return tree.query_condition(field.model._meta.pk, 'isnull', False,
                                    model=field.model)

    def _condition(self, field, operator, value, tree):
        """Builds a `Q` object for `field` relative to `tree`.
        This handles a few edge cases such as passing a `None` in the list
        of values for an 'in' lookup and ensuring lookups for NULL values do
        not include filled in rows. Read more in `_get_not_null_pk`.
        """

        # Ensure this is a ModelTree instance
        tree = trees[tree]

        # Define condition
        condition = None

        # Flag for adding a condition with includes querying for a NULL value
        add_null = False

        value = self._normalize_value(field, value)

        # Assuming the operator and value validate, check for a NoneType value
        # if the operator is 'in'. This condition will be broken out into a
        # separate Q object
        if operator.lookup == 'exact' and value is None:
            add_null = True
        elif operator.lookup == 'isnull':
            add_null = True
        else:
            # Remove the None value from the list to process separately
            if operator.lookup == 'in':
                if None in value:
                    add_null = True
                    value.remove(None)

            # Process a normal value
            if value is not None:
                condition = \
                    tree.query_condition(field.field, operator.lookup, value,
                                         model=field.model)

            # Reset value to None for `null` processing
            value = None

        # The logical OR here is harmless since the only time where a previous
        # condition is defined is for an 'in' lookup.
        if add_null:
            # If value is None, this defaults to isnull=True
            if value is None:
                value = True
            # Read the _get_not_null_pk docs for more info
            null_condition = tree.query_condition(field.field, 'isnull', value,
                                                  model=field.model)

            if field.model is not tree.root_model:
                null_condition = null_condition & \
                    self._get_not_null_pk(field, tree)

            # Tack on to the existing condition if one is defined
            if condition is not None:
                condition = condition | null_condition
            else:
                condition = null_condition

        if operator.negated:
            return ~condition
        return condition

    def _normalize_value(self, field, value):
        """Normalizes a cleaned value from some non-primitive type
        such as a model or queryset instance.
        """
        if field.simple_type == 'key':
            if isinstance(value, (list, tuple, QuerySet)):
                return [x.pk for x in value]
            return value.pk
        if isinstance(value, QuerySet):
            return [x.pk for x in value]
        if isinstance(value, models.Model):
            return value.pk
        return value

    def validate(self, field, operator, value, tree, **kwargs):
        value = self._get_value(value)
        operator = self._validate_operator(field, operator, **kwargs)

        # This is unique case since the operator is driving the required
        # type rather than using the datatype of the field. There is likely
        # a more elegant way to do this.
        if operator.lookup != 'isnull':
            value = self._validate_value(field, value, **kwargs)

        _value = self._normalize_value(field, value)
        if not operator.is_valid(_value):
            raise ValidationError(u'"{0}" is not valid for the operator '
                                  '"{1}"'.format(value, operator))

        return operator, value

    def language(self, field, operator, value, **kwargs):
        return u'{0} {1}'.format(field.name, operator.text(value))

    def translate(self, field, roperator, rvalue, tree, **kwargs):
        """Returns two types of queryset modifiers including:
            - the raw operator and value supplied
            - the validated and cleaned data
            - a Q object containing the condition (or multiple)
            - a dict of annotations to be used downstream

        It should be noted that no checks are performed to prevent the same
        name being used for annotations.
        """
        operator, value = \
            self.validate(field, roperator, rvalue, tree, **kwargs)
        condition = self._condition(field, operator, value, tree)
        language = self.language(field, operator, value, **kwargs)

        return {
            'field': field.pk,
            'operator': roperator,
            'value': rvalue,
            'cleaned_data': {
                'value': value,
                'operator': operator,
                'language': language,
            },
            'query_modifiers': {
                'condition': condition,
                'annotations': None,
                'extra': None,
            }
        }


registry = loader.Registry(default=Translator)

# this will be invoked when it is imported by models.py to use the
# registry choices
loader.autodiscover('translators')

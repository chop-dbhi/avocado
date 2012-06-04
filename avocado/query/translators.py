from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from modeltree.tree import trees
from avocado.core import loader
from avocado.conf import settings
from avocado.core.utils import get_form_class
from .operators import registry as operators

DEFAULT_OPERATOR = 'exact'
DATATYPE_OPERATOR_MAP = settings.DATATYPE_OPERATOR_MAP
INTERNAL_DATATYPE_FORMFIELDS = settings.INTERNAL_DATATYPE_FORMFIELDS


class OperatorNotPermitted(Exception):
    pass


class Translator(object):
    "The base translator class that all translators must subclass."

    # An override of the list of supported operators for this particular
    # translator. This may be necessary for client programs which have
    # custom representations for certain fields.
    operators = None

    # Override of the field's field's default formfield class to be
    # used for validation. this is usually never necessary to override
    form_class = None

    def get_operators(self, datafield):
        # Determine list of allowed operators
        return self.operators or DATATYPE_OPERATOR_MAP[datafield.datatype]

    def _validate_operator(self, datafield, uid, **kwargs):
        # Determine list of allowed operators
        allowed_operators = self.get_operators(datafield)
        uid = uid or allowed_operators[0]

        # Attempt to retrieve the operator. no exception handling for
        # this step exists since this should never fail
        operator = operators.get(uid)

        # No operator is registered
        if operator is None:
            raise ValueError('"{0}" is not a valid operator'.format(uid))

        # Ensure the operator is allowed
        if operator.uid not in allowed_operators:
            raise OperatorNotPermitted('Operator "{0}" cannot be used for this translator'.format(operator))
        return operator

    def _validate_value(self, datafield, value, lookup_value=False, **kwargs):
        # If a form class is not specified, check to see if there is a custom
        # form_class specified for this datatype or if this translator has
        # one defined
        if 'form_class' not in kwargs:
            datatype = datafield.datatype
            if self.form_class:
                kwargs['form_class'] = self.form_class
            elif datatype in INTERNAL_DATATYPE_FORMFIELDS:
                name = INTERNAL_DATATYPE_FORMFIELDS[datatype]
                kwargs['form_class'] = get_form_class(name)

        # If this datafield is flagged as enumerable, use a select multiple
        # by default.
        if lookup_value and datafield.enumerable and 'widget' not in kwargs:
            kwargs['widget'] = forms.SelectMultiple(choices=datafield.choices)

        # Since None is considered an empty value by the django validators
        # ``required`` has to be set to False to not raise a ValidationError
        # saying the field is required. There may be a need to more explicitly
        # check to see if the value be passed is only None and not any of the
        # other empty values in ``django.core.validators.EMPTY_VALUES``
        if datafield.field.null:
            kwargs['required'] = False

        # Get the default formfield for the model field
        formfield = datafield.field.formfield(**kwargs)

        # special case for ``None`` values since all form fields seem to handle
        # the conversion differently. simply ignore the cleaning if ``None``,
        # this scenario occurs when a list of values are being queried and one
        # of them is to lookup NULL values
        if hasattr(value, '__iter__'):
            new_value = []
            for x in value:
                if x is not None:
                    new_value.append(formfield.clean(x))
                # Django assumes an empty string when given a ``NoneType``
                # for char-based form fields, this is to ensure ``NoneType``
                # are passed through unmodified
                else:
                    new_value.append(None)
            return new_value
        return formfield.clean(value)

    def _get_not_null_pk(self, field, tree):
        # XXX The below logic is required to get the expected results back
        # when querying for NULL values. Since NULL can be a value and a
        # placeholder for non-existent values, then a condition to ensure
        # the row's primary key is also NOT NULL must be added. Django
        # assumes in all cases when querying on a NULL value all joins in
        # the chain up to that point must be promoted to LEFT OUTER JOINs,
        # which could be a reasonable assumption for some cases, but for
        # getting the existent rows of data back for our purposes, the
        # assumption is wrong. The conditions defined for the query are not
        # necessarily going to also be the data selected

        # If this field is already the primary key, then don't bother
        # adding this condition, since it would be redundant
        if field.primary_key:
            return Q()

        pk_field = field.model._meta.pk
        key = trees[tree].query_string_for_field(pk_field, 'isnull')

        return Q(**{key: False})

    def _condition(self, datafield, operator, value, tree):
        tree = trees[tree]
        field = datafield.field
        same_model = tree.root_model is field.model

        # Assuming the operator and value validate, check for a NoneType value
        # if the operator is 'in'. This condition will be broken out into a
        # separate Q object
        if operator.operator == 'in' and None in value:
            value = value[:]
            value.remove(None)

            key = trees[tree].query_string_for_field(field, 'isnull')

            # simplifies the logic here for a cleaner query. the latter
            # condition allows for null values for the specified column, so
            # we must enforce the additional condition of not letting the
            # primary keys be null. this mimics an INNER JOINs behavior. see
            # ``_get_not_null_pk`` above
            if operator.negated:
                condition = Q(**{key: False}) & self._get_not_null_pk(field, tree)
            else:
                condition = Q(**{key: True})

            # finally, if there are any more values in the list, we include
            # them here
            if value:
                key = trees[tree].query_string_for_field(field, operator.operator)
                condition = Q(**{key: value}) | condition

        else:
            # The statement 'foo=None' is equivalent to 'foo__isnull=True'
            if (operator.operator == 'isnull' or (operator.operator == 'exact' and value is None)):
                key = trees[tree].query_string_for_field(field, 'isnull')

                # Now that isnull is being used instead, set the value to True
                if value is None:
                    value = True

                # If this is -isnull, we need to switch the value
                if operator.negated:
                    value = not value

                condition = Q(**{key: value})

                # again, we need to account for the LOJ assumption
                if value is False and not same_model:
                    condition = condition & self._get_not_null_pk(field, tree)

            # handle all other conditions
            else:
                key = trees[tree].query_string_for_field(field, operator.operator)
                condition = Q(**{key: value})
                if not same_model:
                    condition = condition & self._get_not_null_pk(field, tree)

                condition = ~condition if operator.negated else condition

        return condition

    def validate(self, datafield, operator, value, tree, **kwargs):
        # ensures the operator is valid for the 
        operator = self._validate_operator(datafield, operator, **kwargs)
        value = self._validate_value(datafield, value, **kwargs)

        if not operator.is_valid(value):
            raise ValidationError('"{0}" is not valid for the operator "{1}"'.format(value, operator))

        return operator, value

    def translate(self, datafield, roperator, rvalue, tree, **kwargs):
        """Returns two types of queryset modifiers including:
            - the raw operator and value supplied
            - the validated and cleaned data
            - a Q object containing the condition (or multiple)
            - a dict of annotations to be used downstream

        It should be noted that no checks are performed to prevent the same
        name being used for annotations.
        """
        operator, value = self.validate(datafield, roperator, rvalue, tree, **kwargs)
        condition = self._condition(datafield, operator, value, tree)

        meta = {
            'condition': condition,
            'annotations': None,
            'extra': None,
            'cleaned_data': {
                'operator': operator,
                'value': value
            },
            'raw_data': {
                'operator': roperator,
                'value': rvalue,
            }
        }

        return meta


registry = loader.Registry(default=Translator)

# this will be invoked when it is imported by models.py to use the
# registry choices
loader.autodiscover('translators')

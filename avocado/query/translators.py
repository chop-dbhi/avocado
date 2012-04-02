from django.db.models import Q
from django.core.exceptions import ValidationError

from avocado.query.operators import registry as operators
from avocado.core import loader
from avocado.conf import settings

DEFAULT_OPERATOR = 'exact'
DATATYPE_OPERATOR_MAP = settings.DATATYPE_OPERATOR_MAP

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

    def __call__(self, *args, **kwargs):
        return self.translate(*args, **kwargs)

    def _validate_operator(self, datafield, uid, **kwargs):
        # Determine list of allowed operators
        allowed_operators = self.operators or DATATYPE_OPERATOR_MAP[datafield.datatype]
        uid = uid or allowed_operators[0]

        # Attempt to retrieve the operator. no exception handling for
        # this step exists since this should never fail
        operator = operators.get(uid)

        # No operator is registered
        if operator is None:
            raise ValueError('"{0}" is not a valid operator'.format(uid))

        # Ensure the operator is allowed
        if operator.uid not in allowed_operators:
            raise OperatorNotPermitted('operator "{0}" cannot be used for this translator'.format(operator))

        return operator

    def _validate_value(self, datafield, value, **kwargs):
        if self.form_class:
            kwargs.setdefault('form_class', self.form_class)

        # TODO since None is considered an empty value by the django validators
        # ``required`` has to be set to False to not raise a ValidationError
        # saying the field is required. There may be a need to more explicitly
        # check to see if the value be passed is only None and not any of the
        # other empty values in ``django.core.validators.EMPTY_VALUES``
        if datafield.field.null:
            kwargs['required'] = False

        formfield = datafield.formfield(**kwargs)

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

    def _get_not_null_pk(self, datafield, using):
        # XXX the below logic is required to get the expected results back
        # when querying for NULL values. since NULL can be a value and a
        # placeholder for non-existent values, then a condition to ensure
        # the row's primary key is also NOT NULL must be added. Django
        # assumes in all cases when querying on a NULL value all joins in
        # the chain up to that point must be promoted to LEFT OUTER JOINs,
        # which could be a reasonable assumption for some cases, but for
        # getting the existent rows of data back for our purposes, the
        # assumption is wrong. the conditions defined for the query are not
        # necessarily going to also be the data selected

        # if this field is already the primary key, then don't bother
        # adding this condition, since it would be redundant
        if datafield.field.primary_key:
            return Q()

        from avocado.models import DataField
        pk_name = datafield.model._meta.pk.name

        # instantiate a new object to utilize the shortcut methods
        _field = DataField(app_name=datafield.app_name, model_name=datafield.model_name, field_name=pk_name)
        key = _field.query_string('isnull', using=using)

        return Q(**{key: False})

    def _condition(self, datafield, operator, value, using):
        # assuming the operator and value validate, check for a NoneType value
        # if the operator is 'in'. This condition will be broken out into a
        # separate Q object
        if operator.operator == 'in' and None in value:
            value = value[:]
            value.remove(None)

            key = datafield.query_string('isnull', using=using)

            # simplifies the logic here for a cleaner query. the latter
            # condition allows for null values for the specified column, so
            # we must enforce the additional condition of not letting the
            # primary keys be null. this mimics an INNER JOINs behavior. see
            # ``_get_not_null_pk`` above 
            if operator.negated:
                condition = Q(**{key: False}) & self._get_not_null_pk(datafield, using)
            else:
                condition = Q(**{key: True})

            # finally, if there are any more values in the list, we include
            # them here
            if value:
                key = datafield.query_string(operator.operator, using=using)
                condition = Q(**{key: value}) | condition

        else:
            # The statement 'foo=None' is equivalent to 'foo__isnull=True'
            if (operator.operator == 'isnull' or (operator.operator == 'exact' and value is None)):
                key = datafield.query_string('isnull', using=using)

                # Now that isnull is being used instead, set the value to True
                if value is None:
                    value = True

                # If this is -isnull, we need to switch the value
                if operator.negated:
                    value = not value

                condition = Q(**{key: value})

                # again, we need to account for the LOJ assumption
                if value is False:
                    condition = condition & self._get_not_null_pk(datafield, using)

            # handle all other conditions
            else:
                key = datafield.query_string(operator.operator, using=using)
                condition = Q(**{key: value}) & self._get_not_null_pk(datafield, using)

                condition = ~condition if operator.negated else condition

        return condition

    def validate(self, datafield, operator, value, **kwargs):
        # ensures the operator is valid for the 
        operator = self._validate_operator(datafield, operator)
        value = self._validate_value(datafield, value)

        if not operator.is_valid(value):
            raise ValidationError('"%s" is not valid for the operator "%s"' %
                (value, operator))

        return operator, value

    def translate(self, datafield, roperator, rvalue, using, **context):
        """Returns two types of queryset modifiers including:
            - the raw operator and value supplied
            - the validated and cleaned data
            - a Q object containing the condition (or multiple)
            - a dict of annotations to be used downstream

        It should be noted that no checks are performed to prevent the same
        name being used for annotations.
        """
        operator, value = self.validate(datafield, roperator, rvalue, **context)
        condition = self._condition(datafield, operator, value, using)

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

from django import forms
from django.db.models import Q

from avocado.exceptions import ValidationError
from avocado.conf import settings
from avocado.concepts.library import Library
from avocado.fields.operators import MODEL_FIELD_MAP
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS
from avocado.utils.iter import ins

class OperatorNotPermitted(Exception):
    pass


class AbstractTranslator(object):
    "The base translator class that all translators must subclass."
    operators = None
    formfield = None

    formfield_overrides = {
        'IntegerField': forms.FloatField,
        'AutoField': forms.IntegerField
    }

    def __call__(self, field, operator=None, value=None, using=DEFAULT_MODELTREE_ALIAS, **context):
        return self.translate(field, operator, value, using=using, **context)

    def _clean_operator(self, field, operator, **kwargs):
        if self.operators:
            operators = self.operators
        else:
            operators = MODEL_FIELD_MAP.get(field.field.__class__.__name__)
        operators = dict([(x.uid, x) for x in operators])

        if not operators.has_key(operator):
            raise OperatorNotPermitted, 'operator "%s" cannot be used for this translator' % operator
        return operators[operator]

    def _clean_value(self, field, value, **kwargs):
        formfield = None

        # has highest precedence if defined on the class. this is usually NOT
        # necessary
        if self.formfield:
            formfield = self.formfield
        # special case for handling standalone ``None`` or ``bool`` values.
        # this occurs when a field is can be queried as a null value, i.e.
        # '-?isnull' : (True|False) or '-?exact' : None
        elif value is None or type(value) is bool:
            formfield = forms.NullBooleanField

        # create an instance of the formfield "to be" and determine if there is
        # a mapping listed for it. TODO make more elegant
        else:
            formfield = field.formfield

            if formfield() is None:
                name = field.field.__class__.__name__
            else:
                name = formfield().__class__.__name__

            if self.formfield_overrides.has_key(name):
                formfield = self.formfield_overrides[name]

        # TODO since None is considered an empty value by the django validators
        # ``required`` has to be set to False to not raise a ValidationError
        # saying the field is required. There may be a need to more explicitly
        # check to see if the value be passed is only None and not any of the
        # other empty values in ``django.core.validators.EMPTY_VALUES``
        ff = field.formfield(formfield=formfield, required=False, **kwargs)

        # special case for ``None`` values since all form fields seem to handle
        # the conversion differently. simply ignore the cleaning if ``None``,
        # this scenario occurs when a list of values are being queried and one
        # of them is to lookup NULL values
        if ins(value):
            new_value = []
            unique_values = set([])
            for x in value:
                if x in unique_values:
                    continue
                unique_values.add(x)
                if x is not None:
                    new_value.append(ff.clean(x))
                # Django assumes an empty string when given a ``NoneType``
                # for char-based form fields, this is to ensure ``NoneType``
                # are passed through unmodified
                else:
                    new_value.append(None)
            return new_value
        return ff.clean(value)

    def _get_not_null_pk(self, field, using):
        # XXX the below logic is required to get the expected results back
        # when querying for NULL values. since NULL can be a value and a
        # placeholder for non-existent values, then a condition to ensure
        # the row's primary key is also NOT NULL must be added. Django
        # assumes in all cases when querying on a NULL value all joins in
        # the chain up to that point must be promoted to LEFT OUTER JOINs,
        # which could be a reasonable assumption for some cases, but for
        # getting the existent rows of data back for our purposes, the
        # assumption is wrong.

        # if this field is already the primary key, then don't bother
        # adding the test, since it would be redundant
        if field.field.primary_key:
            return Q()

        from avocado.models import Field
        pk_name = field.model._meta.pk.name

        pk_field = Field(app_name=field.app_name,
            model_name=field.model_name, field_name=pk_name)

        key = pk_field.query_string('isnull', using=using)

        return Q(**{key: False})

    def _condition(self, field, operator, value, using):
        # assuming the operator and value validate, check for a NoneType value
        # if the operator is 'in'. This condition will be broken out into a
        # separate Q object
        if operator.operator == 'in' and None in value:
            value = value[:]
            value.remove(None)

            key = field.query_string('isnull', using=using)

            if operator.negated:
                condition = Q(**{key: False})
            else:
                condition = Q(**{key: True}) & self._get_not_null_pk(field, using)

            if value:
                key = field.query_string(operator.operator, using=using)
                condition = Q(**{key: value}) | condition
        else:
            if (operator.operator == 'isnull' or
                (operator.operator == 'exact' and value is None)):

                key = field.query_string('isnull', using=using)
                value = not operator.negated

                condition = Q(**{key: value})

                if value is True:
                    condition = condition & self._get_not_null_pk(field, using)
            else:
                key = field.query_string(operator.operator, using=using)
                condition = Q(**{key: value})

                condition = ~condition if operator.negated else condition

        return condition

    def validate(self, field, operator, value, **kwargs):
        clean_op = self._clean_operator(field, operator)
        clean_val = self._clean_value(field, value)
        if not clean_op.check(clean_val):
            raise ValidationError, '"%s" is not valid for the operator "%s"' % (clean_val, clean_op)
        return clean_op, clean_val

    def translate(self, field, roperator, rvalue, using, **context):
        """Returns two types of queryset modifiers including:
            - a Q object applied via the `filter()' method
            - a dict of annotations

        It should be noted that no checks are performed to prevent the same
        name being used for annotations.
        """
        operator, value = self.validate(field, roperator, rvalue, **context)
        condition = self._condition(field, operator, value, using)

        meta = {
            'condition': condition,
            'annotations': {},
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


class DefaultTranslator(AbstractTranslator):
    "Provides the default behavior of creating a simple lookup."
    pass


class TranslatorLibrary(Library):
    superclass = AbstractTranslator
    module_name = settings.TRANSLATOR_MODULE_NAME
    suffix = 'Translator'
    default = DefaultTranslator()


library = TranslatorLibrary()
library.autodiscover()

from django.db.models import Q
from django.forms import FloatField

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
        'IntegerField': FloatField
    }

    def __call__(self, field, operator=None, value=None, using=DEFAULT_MODELTREE_ALIAS, **context):
        return self.translate(field, operator, value, using=using, **context)

    def _clean_operator(self, field, operator):
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
        if self.formfield:
            formfield = self.formfield
        else:
            name = field.formfield().__class__.__name__
            if self.formfield_overrides.has_key(name):
                formfield = self.formfield_overrides[name]

        ff = field.formfield(formfield=formfield, **kwargs)

        if ins(value):
            return map(ff.clean, value)
        return ff.clean(value)

    def validate(self, field, operator, value):
        clean_op = self._clean_operator(field, operator)
        clean_val = self._clean_value(field, value)
        if not clean_op.check(clean_val):
            raise ValidationError, '"%s" is not valid for the operator "%s"' % (clean_val, clean_op)
        return clean_op, clean_val

    def translate(self, field, operator, value, using, **context):
        """Returns two types of queryset modifiers including:
            - a Q object applied via the `filter()' method
            - a dict of annotations

        It should be noted that no checks are performed to prevent the same
        name being used for annotations.
        """
        operator, value = self.validate(field, operator, value)
        key = field.query_string(operator.operator, using=using)
        kwarg = {key: value}

        if operator.negated:
            return ~Q(**kwarg), {}
        return Q(**kwarg), {}


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

from django.db.models import Q

from avocado.exceptions import ValidationError
from avocado.conf import settings
from avocado.concepts.library import Library
from avocado.fields.operators import MODEL_FIELD_MAP
from avocado.utils.iter import is_iter_not_string

class OperatorNotPermitted(Exception):
    pass


class AbstractTranslator(object):
    "The base translator class that all translators must subclass."
    operators = None
    formfield = None

    def __call__(self, modeltree, field, operator=None, value=None, **context):
        self._setup(field)
        try:
            return self.translate(modeltree, field, operator, value, **context)
        finally:
            self._cleanup()
    
    def _setup(self, field):
        operators = self.operators
        formfield = field.formfield

        if not operators:
            operators = MODEL_FIELD_MAP.get(field.field.__class__.__name__)

        self._operators = dict([(x.uid, x) for x in operators])
        self._formfield = formfield
    
    def _cleanup(self):
        hasattr(self, '_operators') and delattr(self, '_operators')
        hasattr(self, '_formfield') and delattr(self, '_formfield')

    def _clean_operator(self, operator):
        if not self._operators.has_key(operator):
            raise OperatorNotPermitted, 'operator "%s" cannot be used for this translator' % operator
        return self._operators[operator]

    def _clean_value(self, value, **kwargs):
        field = self._formfield(**kwargs)
        if is_iter_not_string(value):
            return map(field.clean, value)
        return field.clean(value)

    def validate(self, operator, value):
        clean_op = self._clean_operator(operator)
        clean_val = self._clean_value(value)
        if not clean_op.check(clean_val):
            raise ValidationError, '"%s" is not valid for the operator "%s"' % (clean_val, clean_op)
        return clean_op, clean_val

    def translate(self, modeltree, field, operator, value, **context):
        """Returns two types of queryset modifiers including:
            - a Q object applied via the `filter()' method
            - a dict of annotations
            
        It should be noted that no checks are performed to prevent the same
        name being used for annotations.
        """
        raise NotImplementedError


class DefaultTranslator(AbstractTranslator):
    "Provides the default behavior of creating a simple lookup."    
    def translate(self, modeltree, field, operator, value, **context):
        operator, value = self.validate(operator, value)
        key = field.query_string(modeltree, operator.operator)
        kwarg = {key: value}
        
        if operator.negated:
            return ~Q(**kwarg), {}
        return Q(**kwarg), {}


class TranslatorLibrary(Library):
    superclass = AbstractTranslator
    module_name = settings.TRANSLATOR_MODULE_NAME
    suffix = 'Translator'
    default = DefaultTranslator()


library = TranslatorLibrary()
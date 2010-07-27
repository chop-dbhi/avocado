from django.db.models import Q

from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary
from avocado.fields.operators import *
from avocado.fields.fieldtypes import MODEL_FIELD_MAP
from avocado.utils.iter import is_iter_not_string

class OperatorNotPermitted(Exception):
    pass


class AbstractTranslator(object):
    "The base translator class that all translators must subclass."
    operators = None
    formfield = None

    def __call__(self, modelfield, operator, value, modeltree=None, **kwargs):
        fieldtype = MODEL_FIELD_MAP[modelfield.field.__class__.__name__]

        if not self.operators:
            self.operators = fieldtype.operators
        if not self.formfield:
            self.formfield = fieldtype.formfield
        return self.translate(modelfield, operator, value, modeltree, **kwargs)

    def _get_operators(self):
        if not hasattr(self, '__operators'):
            self.__operators = dict([(x.uid, x) for x in self.operators])
        return self.__operators
    _operators = property(_get_operators)

    def _clean_operator(self, operator):
        if not self._operators.has_key(operator):
            raise OperatorNotPermitted, 'operator "%s" cannot be used for this translator' % operator
        return self._operators[operator].operator

    def _clean_value(self, value):
        field = self.formfield()
        if is_iter_not_string(value):
            return map(field.clean, value)
        return field.clean(value)

    def validate(self, operator, value):
        clean_op = self._clean_operator(operator)
        clean_val = self._clean_value(value)
        return clean_op, clean_val

    def translate(self, modelfield, operator, value, modeltree, **kwargs):
        raise NotImplementedError


class DefaultTranslator(AbstractTranslator):
    def translate(self, modelfield, operator, value, modeltree, **kwargs):
        operator, value = self.validate(operator, value)
        key = modelfield.query_string(operator, modeltree)
        kwarg = {key: value}
        return Q(**kwarg)


class TranslatorLibrary(BaseLibrary):
    "The base class for defining the translator library."
    STORE_KEY = 'translators'
    
    default = DefaultTranslator()

    def _get_store(self, key=None):
        return self._cache

    def _fmt_name(self, name):
        return super(TranslatorLibrary, self)._fmt_name(name, 'Translator')

    def _register(self, klass_name, obj):
        self._add_item(None, klass_name, obj)

    def register(self, klass):
        return super(TranslatorLibrary, self).register(klass, AbstractTranslator)

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache.keys()]
    
    def get(self, name):
        return super(TranslatorLibrary, self).get(None, name)


library = TranslatorLibrary()

# find all other translators
library.autodiscover(avs.TRANSLATOR_MODULE_NAME)

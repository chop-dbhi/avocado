import imp

from django.db.models import Q

from avocado.exceptions import AlreadyRegisteredError, RegisterError
from django.utils.importlib import import_module

class AbstractFilter(object):
    """Provides the logic necessary to return a Q object for altering a
    QuerySet object.

    There are 3 components necessary for specifying conditions:
        - the ModelTree object
        - CriterionConcept fields
        - the logic tree
    """
    def __call__(self, *args, **kwargs):
        return self.filter(*args, **kwargs)

    def _clean(self, field, value, *args, **kwargs):
        "Cleans `value' according to `field'."
        is_valid, cleaned_value, errors = field.clean_value(value, *args, **kwargs)
        return cleaned_value

    def _rel_path(self, modeltree, field, operator):
        nodes = modeltree.path_to(field.model)
        return modeltree.query_string(nodes, field.field_name, operator)

    def filter(self, modeltree, field, operator, value):
        raise NotImplementedError


class SimpleFilter(AbstractFilter):
    def filter(self, modeltree, field, operator, value):
        key = self._rel_path(modeltree, field, operator)
        cleaned_value = self._clean(field, value)
        return Q(**{key: cleaned_value})


class FilterLibrary(object):
    "The base class for defining a filter library."
    def __init__(self):
        self._cache = {}

    def _parse_name(self, name):
        if name.endswith('Filter'):
            name = name[:-6]
        toks = [name[0]]
        for x in name[1:]:
            if x.isupper():
                toks.append(' ')
            toks.append(x)
        return ''.join(toks)

    def register(self, klass):
        "Registers a AbstractFilter subclass. The class name must be unique."
        if not issubclass(klass, AbstractFilter):
            raise RegisterError, '%s must be a subclass of AbstractFilter' % \
                repr(klass)

        obj = klass()

        if hasattr(klass, 'name'):
            klass_name = klass.name
        else:
            klass_name = self._parse_name(klass.__name__)

        if self._cache.has_key(klass_name):
            raise AlreadyRegisteredError, 'A filter with the ' \
                'name "%s" is already registered' % klass_name

        self._cache[klass_name] = obj
        return klass

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache.keys()]


library = FilterLibrary()

library.register(SimpleFilter)


LOADING = False

def autodiscover():
    global LOADING

    if LOADING:
        return
    LOADING = True

    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('filters', app_path)
        except ImportError:
            continue

        import_module('%s.filters' % app)

    LOADING = False

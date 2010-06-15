import imp

from django.utils.importlib import import_module

class AlreadyRegisteredError(Exception):
    pass


class RegisterError(Exception):
    pass


class AbstractFilter(object):
    """The AbstractFilter defines the base behavior for altering a QuerySet
    object.
    """
    def __call__(self, negated=False, **kwargs):
        if negated:
            return ~self.filter(**kwargs)
        return self.filter(**kwargs)

    def filter(self, **kwargs):
        "Returns a Q object."
        raise NotImplementedError


class FilterLibrary(object):
    "The base class for defining a filter library."
    def __init__(self, formatter_types={}):
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
                'name "%s" is already registered' % klass.name

        self._cache[klass_name] = obj
        return klass

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache.keys()]

library = FilterLibrary()


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

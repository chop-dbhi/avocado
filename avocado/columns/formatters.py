import imp
from copy import deepcopy

from django.utils.importlib import import_module

from avocado.settings import settings
from avocado.utils.iter import is_iter_not_string

class AlreadyRegisteredError(Exception):
    pass


class RegisterError(Exception):
    pass


class FormatError(Exception):
    pass


class AbstractFormatter(object):
    """The AbstractFormatter defines the base behavior for formatting a set of
    arguments.
    """
    apply_to_all = False
    is_choice = True

    def __call__(self, ftype, *args):
        return getattr(self, ftype)(*args)


class RemoveFormatter(AbstractFormatter):
    "Overrides default behavior. Returns an empty list; removing the output."
    apply_to_all = True
    is_choice = False

    def __call__(self, ftype, *args):
        return []


class IgnoreFormatter(AbstractFormatter):
    "Overrides default behavior. Simple retruns the args as-is."
    apply_to_all = True
    is_choice = False

    def __call__(self, ftype, *args):
        return args


class FormatterLibrary(object):
    """The base class for defining a formatter library.

    This library dynamically determines the available formatter types via a
    user-defined setting `COLUMN_CONCEPT_FORMATTER_TYPES'. This provides the
    available to define any number of formatter types without needing to
    subclass or override any part of the library. An example as follows:

        FORMATTER_TYPES = {
            'json': {
                'error': '[data format error]',
            },
            'html' : {
                'error': '<span class="data-format-error">[data format error]</span>',
                'null': '<span class="lg ht">(no data)</span>',
            },
            'csv': {
                'error': '[data format error]',
                'null': '',
            }
        }

    Every formatter registered must be a sublcass of the AbstractFormatter
    class. Each formatter can support any number of formatter types by simply
    defining a method of the same name, e.g:

        class MyFormatter(AbstractFormatter):
            def json(*args):
                return ' '.join(map(lambda x: str(x).upper(), args))

    The above formatter class supports the "json" formatter type but not
    either of the "html" or "csv" types. For formatters that need to support
    more than one type, but handles the input the same, the following
    convention should be used:

        class MyFormatter(AbstractFormatter):
            def json(*args):
                return ' '.join(map(lambda x: str(x).upper(), args))
            html = json

    The "html" formatter merely points to the "json" method.
    """

    FORMATTER_TYPES = settings.FORMATTER_TYPES

    def __init__(self, formatter_types={}):
        self._cache = deepcopy(formatter_types or self.FORMATTER_TYPES)
        for key in self._cache:
            self._cache[key]['formatters'] = {}
        self._ftypes = self._cache.keys()

    def _parse_name(self, name):
        if name.endswith('Formatter'):
            name = name[:-9]
        toks = [name[0]]
        for x in name[1:]:
            if x.isupper():
                toks.append(' ')
            toks.append(x)
        return ''.join(toks)

    def _add_formatter(self, ftype, klass_name, obj):
        if self._cache[ftype]['formatters'].has_key(klass_name):
            raise AlreadyRegisteredError, 'A formatter with the ' \
                'name "%s" is already registered for the %s ' \
                'formatter type' % (klass_name, ftype)
        self._cache[ftype]['formatters'][klass_name] = obj

    def register(self, klass):
        "Registers a Formatter subclass. The class name must be unique."
        if not issubclass(klass, AbstractFormatter):
            raise RegisterError, '%s must be a subclass of AbstractFormatter' % repr(klass)

        obj = klass()

        if hasattr(klass, 'name'):
            klass_name = klass.name
        else:
            klass_name = self._parse_name(klass.__name__)

        for ftype in self._ftypes:
            if hasattr(obj, ftype) or obj.apply_to_all: # strange requirement?
                self._add_formatter(ftype, klass_name, obj)
        return klass

    def choices(self, ftype):
        "Returns a list of tuples that can be used as choices in a form."
        choices = []
        for name, obj in self._cache[ftype]['formatters'].items():
            if obj.is_choice:
                choices.append((name, name))
        return choices

    def format_seq(self, seq, rules, ftype, formatters, error, null):
        n, toks = 0, []

        for fname, nargs in rules:
            args = seq[n:n+nargs]

            try:
                obj = formatters[fname]
                tok = obj(ftype, *args)
            except Exception:
                tok = error

            if is_iter_not_string(tok):
                tok = list(tok)
                for i, t in enumerate(iter(tok)):
                    if t is None:
                        tok[i] = null
                toks.extend(tok)
            else:
                if tok is None:
                    tok = null
                toks.append(tok)

            n += nargs

        # all args have not been processed, therefore mixed formatting may have
        # occurred.
        if n != len(seq):
            raise FormatError, 'The rules "%s" is being applied to a ' \
                'sequence of %d items' % (rules, len(seq))

        return tuple(toks)

    def format(self, iterable, rules, ftype):
        """Take an iterable and formats the data given the rules.

        Definitions:

            `iterable' - an iterable of iterables

            `rules' - a list of pairs defining the formatter name and the
            number of items to format, e.g. [('MyFormatter', 3),
            ('AnotherFormatter', 1)]

            `ftype' - a string specifying the formatter type

                class MyFormatter(AbstractFormatter):
                    def json(*args):
                        return ' '.join(map(lambda x: str(x).upper(), args))

                iterable    = [(3, 'foo', 746, 'bar', 392)]
                rules       = (2, 'My')
                ftype       = 'json'

                The result will be:

                    [(3, 'FOO', '848', 'BAR', 392)]
        """
        formatters = self._cache[ftype]['formatters']
        error = self._cache[ftype].get('error', '')
        null = self._cache[ftype].get('null', None)
        
        for seq in iter(iterable):
            yield self.format_seq(seq, rules, ftype, formatters, error, null)


library = FormatterLibrary()

library.register(RemoveFormatter)
library.register(IgnoreFormatter)


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
            imp.find_module('formatters', app_path)
        except ImportError:
            continue

        import_module('%s.formatters' % app)

    LOADING = False

autodiscover()

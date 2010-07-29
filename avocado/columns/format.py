from copy import deepcopy

from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary
from avocado.utils.iter import is_iter_not_string

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


class FormatterLibrary(BaseLibrary):
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
    STORE_KEY = 'formatters'
    FORMATTER_TYPES = avs.FORMATTER_TYPES

    def __init__(self, formatter_types={}):
        self._cache = deepcopy(formatter_types or self.FORMATTER_TYPES)
        self.format_types = self._cache.keys()

        self._add_store()
    
    def _format_name(self, name):
        return super(FormatterLibrary, self)._format_name(name, 'Formatter')

    def _register(self, klass_name, obj):
        for ftype in self.format_types:
            if hasattr(obj, ftype) or obj.apply_to_all:
                self._add_item(ftype, klass_name, obj)
    
    def register(self, klass):
        return super(FormatterLibrary, self).register(klass, AbstractFormatter)

    def choices(self, ftype):
        "Returns a list of tuples that can be used as choices in a form."
        store = self._get_store(ftype)
        choices = []
        
        for name, obj in store.items():
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

# find all other formatters
library.autodiscover(avs.FORMATTER_MODULE_NAME)
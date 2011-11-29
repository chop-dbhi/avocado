from copy import deepcopy
from django.template import defaultfilters as filters
from avocado.conf import settings
from avocado.exceptions import AlreadyRegisteredError
from avocado.concepts.library import Library
from avocado.utils.iter import ins

class FormatError(Exception):
    pass


class AbstractFormatter(object):
    """The AbstractFormatter defines the base behavior for formatting a set of
    objects.

    Each ``AbstractFormatter`` subclass will be registered with each output
    type if it has an applicable method. For example, if I have defined two
    output types 'json' and 'csv', then the following class will only be
    registered with the 'json' output type::

        class MyFormatter(AbstractFormatter):
            def json(self, *args, **args):
                # ...

    The requirement is that a method on the formatter subclass with the same
    name as the output type is defined. To override this behavior and apply
    a formatter to all output types, set ``apply_to_all`` to true.

    .. note::

        Note that when the formatters are registered, a single object is
        instantiated and registered with each output type. The objects should
        be stateless since the object can be shared.

    """
    apply_to_all = False
    is_choice = True

    def __call__(self, ftype, *args):
        return getattr(self, ftype)(*args)


class RemoveFormatter(AbstractFormatter):
    "Returns an empty list, removing the output."
    apply_to_all = True
    is_choice = False

    def __call__(self, ftype, *args):
        return []


class PassFormatter(AbstractFormatter):
    "Overrides default behavior. Simple retruns the args as-is."
    apply_to_all = True
    is_choice = False

    def __call__(self, ftype, *args):
        return args


class DefaultFormatter(AbstractFormatter):
    def html(self, *args):
        toks = []
        for x in args:
            if x is None: continue
            if type(x) is float:
                t = filters.floatformat(x)
            else:
                t = str(x)
            toks.append(t)
        return ' '.join(toks) or None

    def csv(self, *args):
        return args or None


class FormatterLibrary(Library):
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
    defining a method of the same name, e.g::

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
    superclass = AbstractFormatter
    module_name = settings.FORMATTER_MODULE_NAME
    suffix = 'Formatter'

    def __init__(self, *args, **kwargs):
        super(FormatterLibrary, self).__init__(*args, **kwargs)
        self._cache = deepcopy(settings.FORMATTER_TYPES)
        self.format_types = self._cache.keys()

        for key in self._cache:
            self._cache[key]['formatters'] = {}

    def add_object(self, key, class_name, obj, errmsg=''):
        store = self.get_store()[key]['formatters']
        # if already registered under the same name, test if the classes are
        # the same -- replace if true, throw error if not
        if store.has_key(class_name):
            robj = store.get(class_name)
            if obj.__class__ is not robj.__class__:
                raise AlreadyRegisteredError, errmsg
        store.update({class_name: obj})

    def register_object(self, klass_name, obj):
        for key in self.format_types:
            if hasattr(obj, key) or obj.apply_to_all:
                self.add_object(key, klass_name, obj)

    def choices(self, key):
        "Returns a list of tuples that can be used as choices in a form."
        store = self.get_store()[key]['formatters']
        choices = []

        for name, obj in store.items():
            if obj.is_choice:
                choices.append((name, name))
        return choices

    def format_seq(self, seq, rules, ftype, formatters, error, null):
        n, toks = 0, []

        for fname, nargs in rules:
            args = seq[n:n+nargs]

            # if the formatter expects one argument, but it is None,
            # skip the formatting and default to None.
            if len(args) == 1 and args[0] is None:
                tok = None
            else:
                try:
                    obj = formatters[fname]
                    tok = obj(ftype, *args)
                except Exception:
                    tok = error

            if ins(tok):
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
        store = self.get_store()[ftype]

        formatters = store['formatters']
        error = store.get('error', '')
        null = store.get('null', None)

        for seq in iter(iterable):
            yield self.format_seq(seq, rules, ftype, formatters, error, null)


library = FormatterLibrary()

library.register(RemoveFormatter)
library.register(PassFormatter)
library.register(DefaultFormatter)

library.default = DefaultFormatter()

library.autodiscover()

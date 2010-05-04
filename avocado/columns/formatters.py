"""
The role of the FormatterLibrary register and provide utility for formatters. A
formatter is defined as a callable that has a unique function `func.__name__'
relative to the library it is being registered to.

The receiving end must be kept in mind, since this is effectively re-packaging
the formatted data row by row. It may be useful to subclass FormatterLibrary
and override the `format()' method in order to specify the package format.
"""

# import datetime
from functools import wraps

# from django.utils.importlib import import_module
# from django.template import defaultfilters as filters
# 
# from avocado.utils import conversions

# LOADING = False

# def autodiscover():
#     global LOADING
# 
#     if LOADING:
#         return
#     LOADING = True
# 
#     import imp
#     from django.conf import settings
# 
#     for app in settings.INSTALLED_APPS:
#         try:
#             app_path = import_module(app).__path__
#         except AttributeError:
#             continue
# 
#         try:
#             imp.find_module('formatters', app_path)
#         except ImportError:
#             continue
# 
#         import_module('%s.formatters' % app)
# 
#     LOADING = False
class RegisterError(Exception):
    pass


class FormatterLibrary(object):
    "The base class for defining a formatter library."

    DATA_FORMAT_ERROR = '(data format error)'
    
    def __init__(self):
        self.formatters = {}

    def _default(self, *args):
        "The default formatter if none is supplied or is not registered."
        return ' '.join([str(x) for x in args])

    def register(self, name=None):
        """Registers a callable with this library. The function name must be
        unique.
        """
        def decorator(func):
            key = func.__name__
            if name and callable(name):
                _name = func.__name__
            else:
                _name = name
            
            if self.formatters.has_key(key):
                raise RegisterError, '%s already has a callable registered ' \
                    'by the name %s' % (self.__class__.__name__, _name)

            self.formatters.update({key: (_name, func)})

            def _func(*args, **kwargs):
                return func(*args, **kwargs)
            return wraps(func)(_func)

        if name and callable(name):
            return decorator(name)
        return decorator

    @property
    def choices(self):
        "Convenience property for getting form choices."
        if not hasattr(self, '_choices'):
            self._choices = [(fn, n) for fn, (n, f) in self.formatter.items()]
        return self._choices

    def get(self, name):
        return self.formatters.has_key(name) and self.formatters.get(name)[1] or None

    def format_row(self, item, rules, idx):
        toks = []
        head = idx[0] and list(item[:idx[0]]) or []
        tail = idx[1] and list(item[idx[1]:]) or []
        data = item[idx[0]:idx[1]]
        
        i = 0
        for fname, cnt in rules:
            # skip if the rule does not apply to anything
            if cnt == 0:
                continue
            func = self.get(fname) or self._default
            try:
                tok = func(*data[i:i+cnt])
            except StandardError:
                tok = self.DATA_FORMAT_ERROR
            
            # `extend' toks only if it is an iterable and not a string
            if isinstance(tok, basestring):
                toks.append(tok)
            else:
                try:
                    iter(tok)
                    toks.extend(tok)
                except TypeError:
                    toks.append(tok)
            i += cnt
        return tuple(head + toks + tail)

    def format(self, iterable, rules, idx=(1, None)):
        """Take an iterable and formats the data given the rules.
        
        Definitions:
        
            `iterable' - an iterable of iterables
        
            `rules' - a list of pairs defining the formatter name and the
            number of items to format, e.g. [('foo', 3), ('bar', 1)] 
            
            `idx' - the slice of data to format per row. the data ignored
            will not be passed through the formatter, but will be retained and
            passed back with the the formatted data, e.g:

                def afunc(arg1, arg2):
                    return arg1 + arg2
            
                iterable    = [(3, 102, 746, 'bar', 392)]
                rules       = (2, 'afunc')
                idx         = (1, 3)
                            
                The result will be:
                
                    [(3, 848, 'bar', 392)]
        """        
        for item in iter(iterable):
            yield self.format_row(item, rules, idx)


class DictFormatterLibrary(FormatterLibrary):
    def format_row(self, item, rules, idx, key):
        """Simple override that assumes the items are dictionaries and the raw
        data is accessed via a key.
        """
        item[key] = super(DictFormatterLibrary, self).format_row(item[key], rules, idx)
        return item
    
    def format(self, iterable, rules, idx=(1, None), key='data'):
        for item in iter(iterable):
            yield self.format_row(item, rules, idx, key)


class JSONFormatterLibrary(DictFormatterLibrary):
    DATA_FORMAT_ERROR = '<span class="data-format-error">(data format error)</span>'


# TODO to implementation
 
# @library.register('Date to Age')
# def date_to_age(lib, value):
#     "Expects a date or datetime instance."
#     today = datetime.date.today()
#     if isinstance(value, datetime.datetime):
#         value = value.date()
#     return days_to_age((today-value).days)
# 
# @library.register('Days to Age')
# def days_to_age(lib, value):
#     "Expects a number."
#     return conversions.days_to_age(value)
# 
# @library.register('Years to Age')
# def years_to_age(lib, value):
#     "Expects a number." 
#     return conversions.years_to_age(value)
# 
# @library.register('Bool to Yes/No')
# def yesno(lib, value):
#     "Expects a boolean."
#     if value is True:
#         return 'Yes'
#     elif value is False:
#         return 'No'
#     return
# 
# @library.register('Date')
# def date_format(lib, value):
#     "Expects a date."
#     return filters.date(value)
# 
# autodiscover()

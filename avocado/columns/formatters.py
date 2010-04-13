"""
The FormatterLibrary class manages two distinct types of formatters used
for "raw" data output and "pretty" formatted output. In most cases, a raw data
formatter will not be needed for a typical concept. Exceptions include such
concepts that returns a non-useful piece of data in its raw state or
non-textual data.

A formatter is simply a python function which takes N positional arguemnts.
The default formatter used if no custom formatter is specified is a simple
concatenation function which takes N arguments.

A "pretty" formatter must always return a single representation of those fields
as text or HTML. It is convention to return None if the "pretty" output cannot
be generated.

A "raw" formatter must always return an ordred array of elements, which
contains the formatted values of the fields passed in.
"""
import datetime
from functools import wraps

from django.utils.importlib import import_module
from django.template import defaultfilters as filters

from avocado.utils import conversions

LOADING = False

def autodiscover():
    global LOADING

    if LOADING:
        return
    LOADING = True

    import imp
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

def get_formatters(columns, column_orders):
    """Helper function that formats a set of rows given the formatting
    type.
    """
    from avocado.columns.utils import get_column_fields

    pretty_columns = []
    pretty_formatters = []
    raw_columns = []
    raw_formatters = []

    for column in columns:
        fields = get_column_fields(column)
        display = {
            '_concept': column,
            'id': column.id,
            'name': column.name,
            'direction': '',
            'order': None,
        }
        if column_orders.has_key(column):
            display.update(column_orders[column])

        pretty_columns.append(display)
        pretty_formatters.append((len(fields), column.pretty_formatter))

        if len(fields) > 1:
            raw_columns.extend([x.display_name for x in fields])
        else:
            raw_columns.append(column.name)

        raw_formatters.append((len(fields), column.raw_formatter))

    return (pretty_columns, pretty_formatters, raw_columns, raw_formatters) 


class RegisterError(Exception):
    pass


class FormatterLibrary(object):
    """A simple datastructure that acts as a library for registering and
    managing formatters.
    """
    def __init__(self):
        self._raw_formatters = {}
        self._pretty_formatters = {}

    def register(self, name=None, lib=None):
        """Registers a function as a formatter with an optional name. If `lib'
        is None, then the formatter is registered in both dicts.
        """
        if lib not in (None, 'pretty', 'raw'):
            raise RegisterError, 'you can register to "pretty" or "raw" ' \
                'or None for both'

        def decorator(formatter_func):
            if name and callable(name):
                _name = formatter_func.__name__
            else:
                _name = name

            d = {formatter_func.__name__: (_name, formatter_func)}

            if lib is None or lib == 'raw':
                self._raw_formatters.update(d)
            if lib is None or lib == 'pretty':
                self._pretty_formatters.update(d)

            def _formatter_func(*args):
                return formatter_func(*args)
            return wraps(formatter_func)(_formatter_func)

        if name and callable(name):
            return decorator(name)
        return decorator

    def _get_formatter_dict(self, lib):
        try:
            return getattr(self, '_%s_formatters' % lib)
        except AttributeError:
            raise AttributeError, 'the choice is either "pretty" or "raw"'

    def choices(self, lib):
        "Returns a tuple of pairs that can be used as choices in a form."
        formatter_dict = self._get_formatter_dict(lib)
        return tuple([(x, y[0]) for x, y in formatter_dict.items() if not \
            x.startswith('_')])

    def raw_formatted(self, rows, formatters):
        formatter_dict = self._raw_formatters
        _formatters = []
        # pre-cache the functions
        for cnt, func_name in formatters:
            if formatter_dict.has_key(func_name):
                func = formatter_dict.get(func_name)[1]
            else:
                func = formatter_dict.get('_default_raw')[1]
            _formatters.append((cnt, func))

        for row in rows:
            # assuming the first object is the primary key
            formatted_row = [row[0]]
            start = 1
            for cnt, func in _formatters:
                stop = start + cnt
                vals = row[start:stop]
                # this catches empty values to save a function
                if len(vals) == 1 and vals[0] in (None, ''):
                    new_row = ['']
                else:
                    try:
                        new_row = func('raw', *vals)
                    except StandardError:
                        new_row = ['(data format error)' for i in range(len(cnt))]                 
                    if type(new_row) not in (list, tuple):
                        new_row = [new_row]
                formatted_row.extend(new_row)
                start = stop
            yield formatted_row

    def pretty_formatted(self, rows, formatters):
        "A generator that formats a row at a time."
        formatter_dict = self._pretty_formatters
        _formatters = []
        # pre-cache the functions
        for cnt, func_name in formatters:
            if formatter_dict.has_key(func_name):
                func = formatter_dict.get(func_name)[1]
            else:
                func = formatter_dict.get('_default_pretty')[1]
            _formatters.append((cnt, func))

        for row in rows:
            # assuming the first object is the primary key
            formatted_row = [row[0]]
            start = 1
            for cnt, func in _formatters:
                stop = start + cnt
                vals = row[start:stop]
                if len(vals) == 1 and vals[0] in (None, ''):
                    val = None
                else:
                    try:
                        val = func('pretty', *vals)
                    except StandardError:
                        val = '<span class="format-error">(data format error)</span>'
                formatted_row.append(val)
                start = stop
            yield formatted_row

library = FormatterLibrary()

@library.register('', 'pretty')
def _default_pretty(lib, *vals):
    """The default formatter for a web page view. It should always return
    None if all values are either None or the empty string, which allows for
    a consistent value for displaying web page friendly wording.
    """
    test, fvals = [], []
    for x in vals:
        y = True
        if x in (None, ''):
            x = ''
            y = False
        fvals.append(str(x))
        test.append(y)

    if any(test):
        return ' '.join(fvals)
    return None

@library.register('', 'raw')
def _default_raw(lib, *vals):
    """The default formatter for exporting in a raw format. If a value is
    None, replace it with the empty string.
    """
    fvals = []
    for x in vals:
        if x in (None, ''):
            x = ''
        fvals.append(str(x))
    return tuple(fvals)

@library.register('Date to Age')
def date_to_age(lib, value):
    "Expects a date or datetime instance."
    today = datetime.date.today()
    if isinstance(value, datetime.datetime):
        value = value.date()
    return days_to_age((today-value).days)

@library.register('Days to Age')
def days_to_age(lib, value):
    "Expects a number."
    return conversions.days_to_age(value)

@library.register('Years to Age')
def years_to_age(lib, value):
    "Expects a number." 
    return conversions.years_to_age(value)

@library.register('Bool to Yes/No')
def yesno(lib, value):
    "Expects a boolean."
    if value is True:
        return 'Yes'
    elif value is False:
        return 'No'
    return

@library.register('Date')
def date_format(lib, value):
    "Expects a date."
    return filters.date(value)

autodiscover()
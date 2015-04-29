import logging
from decimal import Decimal
from warnings import warn
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from collections import defaultdict, namedtuple
from django.utils.encoding import force_unicode
from django.template import defaultfilters as filters
from avocado.core import loader

log = logging.getLogger(__name__)


class ExpectedFormatterException(Exception):
    """Exception that can be thrown when an formatter error is expected
    and can be ignored.
    """


class FormatterMismatchError(Exception):
    "Exception raised when the header and the output length do not match."


def _unique_dict(fields):
    """Takes a list of fields and returns an ordered dict with unique keys
    based on the field's natural key.
    """
    def model_prefix(field, key):
        return u'{0}__{1}'.format(field.model_name, key)

    def app_prefix(field, key):
        return u'{0}__{1}'.format(field.app_name, model_prefix(field, key))

    # Evaluate in case this is QuerySet..
    fields = list(fields)

    pairs = []
    names = []
    models = defaultdict(int)

    # Starting set of field names
    for f in fields:
        names.append(f.field_name)
        models[f.model] += 1

    # For consistency, any keys that do conflict, all occurences will
    # be prefixed the same way either with the 'app' or 'model' level
    prefixed = {}

    for i, name in enumerate(names):
        field = fields[i]

        # Check is the prefix is pending
        if name in prefixed:
            key = prefixed[name](field, name)
        elif names.count(name) == 1:
            key = name
        else:
            if models[field.model] == 1:
                key = model_prefix(field, name)
                method = model_prefix
            else:
                key = app_prefix(field, name)
                method = app_prefix

            # Mark this field name to prefixed from now on
            prefixed[name] = method

        pairs.append((key, field))

    return OrderedDict(pairs)


def process_multiple(func):
    "Decorator for marking a formatter method to process multiple values."
    func.process_multiple = True
    return func


class Formatter(object):
    """Converts values into alternate formats, other Python types or
    string-based formats.

    A formatter is initialized and bound to a `concept` with a series of
    `formats` that will be tried when converting the input values. Format
    method are denoted by the `to_` prefix, such as `to_csv`.

    Format methods must return a tuple of values, but may be contain more
    or less values than the original. A `get_FORMAT_header` method must be
    implemented if a custom set of values are being emitted by a format
    method.
    """
    html_delimiter = u' '

    html_map = {
        None: '<em>n/a</em>'
    }

    def __init__(self, concept=None, keys=None, formats=None):
        "Passing in a concept takes precedence over `keys`."
        if not keys and not concept:
            raise ValueError('A concept or sequence of keys are required.')

        self.concept = concept

        if concept:
            self.concept_fields = tuple(concept.concept_fields
                                        .select_related('field')
                                        .order_by('order', 'name'))

            self.fields = _unique_dict(cf.field
                                       for cf in self.concept_fields)
            self.field_names = self.fields.keys()
        else:
            self.concept_fields = ()
            self.fields = {}
            self.field_names = keys

        # Clean formats and split into single vs. multi.
        self.single_formats = []
        self.multi_formats = []

        self.default_context = {}

        if formats:
            for fmt in formats:
                method = getattr(self, 'to_{0}'.format(fmt), None)

                if not method:
                    continue

                if getattr(method, 'process_multiple', False):
                    self.multi_formats.append(method)
                else:
                    self.single_formats.append(method)

        # Keep track of fields/concepts that cause an error to prevent
        # logging the exception twice
        self._errors = set()

        # Create a bare-bones record class.
        self._recordclass = namedtuple('record', self.field_names)

    def __contains__(self, choice):
        return hasattr(self, 'to_{0}'.format(choice))

    def __str__(self):
        return self.__class__.__name__

    def __call__(self, values, context=None):
        "Takes a tuple of values and format it with this prepared formatter."
        if context is None:
            context = self.default_context

        # Create a record of the values.
        record = self._recordclass(*values)

        # Process multi-value format methods first.
        for method in self.multi_formats:
            try:
                output = self._process_multiple(method,
                                                value=record,
                                                context=context)
            except ExpectedFormatterException:
                continue

            return output

        # Optimization. Return raw values if no single-value formatters
        # are being used.
        if not self.single_formats:
            return tuple(record)

        # Process each value separately with the corresponding field.
        output = []

        for i, key in enumerate(record._fields):
            field = self.fields.get(key)

            value = record[i]

            for method in self.single_formats:
                try:
                    value = self._process_single(method,
                                                 value=value,
                                                 field=field,
                                                 context=context)
                except ExpectedFormatterException:
                    continue

                output.extend(value)
                break

            # Fallback to the raw value
            else:
                output.append(record[i])

        return tuple(output)

    def _process_single(self, method, value, field, context):
        output = method(value, field=field, context=context)

        # Backwards compat for dicts.
        if isinstance(output, dict):
            warn('Formatter methods should return a tuple '
                 'of values', DeprecationWarning)

            return tuple(output.values())

        if not isinstance(output, (list, tuple)):
            return (output,)

        return output

    def _process_multiple(self, method, value, context):
        output = method(value, fields=self.fields, context=context)

        # Backwards compat for dicts.
        if isinstance(output, dict):
            warn('Formatter methods should return a tuple '
                 'of values', DeprecationWarning)

            return tuple(output.values())

        if not isinstance(output, (list, tuple)):
            return (output,)

        return output

    def get_default_header(self):
        concept = self.concept

        # If this uses a concept and only has one field, use the concept
        # descriptors for the formatted output.
        if concept:
            if len(self.concept_fields) == 1:
                cf = self.concept_fields[0]
                f = cf.field

                return [{
                    'field': f,
                    'label': str(concept),
                    'name': self.field_names[0],
                    'type': concept.type or f.type or f.simple_type,
                    'description': concept.description or f.description,
                }]

            header = []

            for i, cf in enumerate(self.concept_fields):
                f = cf.field

                header.append({
                    'field': f,
                    'label': str(cf),
                    'name': self.field_names[i],
                    'type': f.type or f.simple_type,
                    'description': f.description,
                })

            return header

        return [{
            'field': None,
            'name': name,
            'label': name,
            'type': None,
            'description': None,
        } for name in self.field_names]

    def get_meta(self, exporter=None):
        """Returns metadata associated with the formatted output.

        The metadata contains references to the concept, concept fields, and a
        header that is a list of meta data per value in the output.

        The `exporter` is passed in since the output may vary depending on
        which exporter is being targeted.
        """
        meta = {
            'concept': self.concept,
            'fields': self.fields.values(),
        }

        # Exporter specific method for building the header.
        header = None

        if exporter:
            method_name = 'get_{0}_header'.format(exporter)
            method = getattr(self, method_name, None)

            if method:
                header = method()

        # Fallback to the default header.
        if header is None:
            header = self.get_default_header()

        meta['header'] = header

        return meta

    # The default HTML method returns a single concatenated value
    # so the header should only contain one field.
    def get_html_header(self):
        return self.get_default_header()[:1]

    @process_multiple
    def to_html(self, values, fields, context):
        toks = []

        for value in values:
            if value is None:
                continue

            # Check the html_map first
            if value in self.html_map:
                tok = self.html_map[value]
            # Prettify floats
            elif type(value) is float:
                tok = filters.floatformat(value)
            else:
                tok = unicode(value)

            toks.append(tok)

        # No values.
        if not toks:
            return self.html_map.get(None, 'N/A')

        return self.html_delimiter.join(toks)

    def to_string(self, value, field, context):
        # Attempt to coerce non-strings to strings. Depending on the data
        # types that are being passed into this, this may not be good
        # enough for certain datatypes or complext data structures
        if value is None:
            return u''

        return force_unicode(value, strings_only=False)

    def to_boolean(self, value, field, context):
        # If value is native True or False value, return it
        if type(value) is bool:
            return value

        raise ExpectedFormatterException('cannot be converted into a boolean')

    def to_number(self, value, field, context):
        # Attempts to convert a number. Starting with ints and floats
        # Eventually create to_decimal using the decimal library.
        if isinstance(value, (int, float)):
            return value

        if isinstance(value, Decimal):
            return float(unicode(value))

        if isinstance(value, basestring):
            if value.isdigit():
                return int(value)

            try:
                return float(value)
            except (ValueError, TypeError):
                pass

        raise ExpectedFormatterException('cannot be converted into a number')

    def to_coded(self, value, field, context):
        # Attempts to convert value to its coded representation
        if field:
            coded_values = field.coded_values()

            if coded_values is not None:
                return coded_values.get(value)

        raise ExpectedFormatterException('field does not support coded values')

    def to_raw(self, value, field, context):
        return value


class RawFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        kwargs.pop('formats', None)
        kwargs['formats'] = ('raw',)

        return super(RawFormatter, self).__init__(*args, **kwargs)


registry = loader.Registry(default=Formatter, register_instance=False)
loader.autodiscover('formatters')

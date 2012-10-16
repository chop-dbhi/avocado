import logging
from collections import OrderedDict, defaultdict
from django.utils.encoding import force_unicode
from avocado.core import loader

log = logging.getLogger(__name__)


class FormatterException(Exception):
    pass


def unique_keys(fields):
    """Takes a list of fields and generated a unique list of keys based
    based on the field's natural_key.
    """
    def model_prefix(field, key):
        return '{}__{}'.format(field.model_name, key)

    def app_prefix(field, key):
        return '{}__{}'.format(field.app_name, model_prefix(field, key))

    # Evaluate in case this is QuerySet..
    fields = list(fields)

    keys = []
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
        keys.append(key)

    return keys


class Formatter(object):
    """Provides support for the core data formats with sensible defaults
    for handling converting Python datatypes to their formatted equivalent.

    Each core format method must return one of the following:
        Single formatted Value
        OrderedDict/sequence of key-value pairs

        If the format method is unable to do either of these for the given
        value a FormatterException must be raised.

        ``values`` - A list, tuple or OrderedDict containing the values to
        be formatted. If a list or tuple is passed, it will be wrapped in
        an OrderedDict for keyword access in the format methods.

        ::

            values = ['Bob', 'Smith']

    """
    default_formats = ('boolean', 'number', 'string')

    def __init__(self, concept=None, keys=None):
        "Passing in a concept takes precedence over `keys`."
        if not keys and not concept:
            raise ValueError('A concept or list of keys must be supplied.')

        self.concept = concept
        self.fields = None

        if concept:
            fields = list(concept.fields.order_by('concept_fields__order'))
            self.keys = unique_keys(fields)
            self.fields = OrderedDict(zip(self.keys, fields))
        else:
            self.keys = keys

    def __call__(self, values, preferred_formats=None, **context):
        # Create a copy of the preferred formats since each set values may
        # be processed slightly differently (e.g. mixed data type in column)
        # which could cause exceptions that would not be present during
        # processing of other values
        if preferred_formats is None:
            preferred_formats = self.default_formats
        preferred_formats = list(preferred_formats) + ['raw']

        # Create a OrderedDict of the values relative to the
        # concept fields objects the values represent. This
        # enables key-based access to the values rather than
        # relying on position.
        if not isinstance(values, OrderedDict):
            # Wrap single values
            if not isinstance(values, (list, tuple)):
                values = [values]
            values = OrderedDict(zip(self.keys, values))

        # Iterate over all preferred formats and attempt to process the values.
        # For formatter methods that process all values must be tracked and
        # attempted only once. They are removed from the list once attempted.
        # If no preferred multi-value methods succeed, each value is processed
        # independently with the remaining formats
        for f in iter(preferred_formats):
            method = getattr(self, 'to_{}'.format(f), None)
            # This formatter does not support this format, remove it
            # from the available list
            if not method:
                preferred_formats.pop(0)
                continue

            # The implicit behavior when handling multiple values is to process
            # them independently since, in most cases, they are not dependent
            # on one another, but rather should be represented together since
            # the data is related. A formatter method can be flagged to process
            # all values together by setting the attribute
            # `process_multiple=True`. we must # check to if that flag has been
            # set and simply pass through the values and context to the method
            # as is. if ``process_multiple`` is not set, each value is handled
            # independently
            if getattr(method, 'process_multiple', False):
                try:
                    output = method(values, fields=self.fields,
                        concept=self.concept, process_multiple=True, **context)
                    if not isinstance(output, dict):
                        return OrderedDict([(self.concept.name, output)])
                    return output
                # Remove from the preferred formats list since it failed
                except Exception:
                    log.exception('Multi-value formatter error')
                    preferred_formats.pop(0)

        # The output is independent of the input. Formatters may output more
        # or less values than what was entered.
        output = OrderedDict()

        # Attempt to process each
        for i, (key, value) in enumerate(values.iteritems()):
            for f in preferred_formats:
                method = getattr(self, 'to_{}'.format(f))
                try:
                    field = self.fields[key] if self.fields else None
                    fvalue = method(value, field=field, concept=self.concept,
                        process_multiple=False, **context)
                    if isinstance(fvalue, dict):
                        output.update(fvalue)
                    else:
                        output[key] = fvalue
                    break
                except Exception:
                    log.exception('Single-value formatter error')
        return output

    def __contains__(self, choice):
        return hasattr(self, 'to_{}'.format(choice))

    def __unicode__(self):
        return u'{}'.format(self.name or self.__class__.__name__)

    def to_string(self, value, **context):
        # Attempt to coerce non-strings to strings. Depending on the data
        # types that are being passed into this, this may not be good
        # enough for certain datatypes or complext data structures
        if value is None:
            return u''
        return force_unicode(value, strings_only=False)

    def to_boolean(self, value, **context):
        # If value is native True or False value, return it
        if type(value) is bool:
            return value
        raise FormatterException('Cannot convert {} to boolean'.format(value))

    def to_number(self, value, **context):
        # Attempts to convert a number. Starting with ints and floats
        # Eventually create to_decimal using the decimal library.
        if type(value) is int or type(value) is float:
            return value
        if isinstance(value, basestring):
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = float(value)
            return value
        raise FormatterException('Cannot convert {} to number'.format(value))

    def to_coded(self, value, **context):
        # Attempts to convert value to its coded representation
        if 'field' in context:
            for key, coded in context['field'].coded_values:
                if key == value:
                    return coded
        raise FormatterException('No coded value for {}'.format(value))

    def to_raw(self, value, **context):
        return value


class RawFormatter(Formatter):
    def __call__(self, values, *args, **kwargs):
        preferred_formats = ['raw']
        return super(RawFormatter, self).__call__(values, preferred_formats)


registry = loader.Registry(default=Formatter, register_instance=False)
loader.autodiscover('formatters')

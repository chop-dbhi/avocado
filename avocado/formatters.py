import logging
from decimal import Decimal
from collections import defaultdict
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.utils.encoding import force_unicode
from avocado.core import loader

log = logging.getLogger(__name__)


class FormatterException(Exception):
    pass


def _unique_keys(fields):
    """Takes a list of fields and generated a unique list of keys based
    based on the field's natural_key.
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

    return pairs


def process_multiple(func):
    "Decorator for marking a formatter method to process multiple values."
    func.process_multiple = True
    return func


class Formatter(object):
    """Converts Python types into a formatted equivalent based on a list of
    `preferred_formats`. If no formats are specified or none of the format
    methods are successful, the default method for the field's type will be
    attempted and finally will fallback to returning the value as is.

    A format is supported if `to_FORMAT` method is defined on the Formatter
    class. By default, the method is assumed to take a value for a single
    field and produce a value. The method signature is:

        def to_FORMAT(value, field=field, concept=self.concept,
                      process_multiple=False, **context)

    With this approach, each field contained in the concept will be processed
    separately.

    Alternately, the method can decorated with `process_multiple` which causes
    the concept and all field values to be passed into the method. The
    signature looks as follows.

        @process_multiple
        def to_FORMAT(values, fields=self.fields, concept=self.concept,
                      process_multiple=True, **context)

    `values` will be an OrderedDict of values for each field. `fields` is
    a map of `DataField` instances associated with `concept` keyed by their
    natural key starting with `field_name` and prepending the `model_name`
    and `app_name` to prevent key collisions.

    The output of a `process_multiple` method can be a single formatted value,
    an OrderedDict, or a sequence of key-value pairs.
    """
    def __init__(self, concept=None, keys=None):
        "Passing in a concept takes precedence over `keys`."
        if not keys and not concept:
            raise ValueError('A concept or sequence of keys are required.')

        self.concept = concept
        self.fields = None

        if concept:
            fields = list(concept.fields.order_by('concept_fields__order'))
            self.fields = OrderedDict(_unique_keys(fields))
            self.keys = self.fields.keys()
        else:
            self.keys = keys

        # Keep track of fields/concepts that cause an error to prevent
        # logging the exception twice
        self._errors = set()

    def __call__(self, values, preferred_formats=None, **context):
        if not preferred_formats:
            preferred_formats = []

        # Create a OrderedDict of the values relative to the
        # concept fields objects the values represent. This
        # enables key-based access to the values rather than
        # relying on position.
        if not isinstance(values, OrderedDict):
            if not isinstance(values, (list, tuple)):
                values = [values]

            values = OrderedDict(zip(self.keys, values))

        # Create list of formats to attempt for multi-value processing.
        multi_formats = list(preferred_formats)

        # Append concept type as a format if one is defined.
        if self.concept and self.concept.type:
            multi_formats.append(self.concept.type)

        multi_formats.append('raw')

        # Iterate over all preferred formats and attempt to process the values.
        # Formatter methods that process all values must be tracked and
        # attempted only once. They are removed from the list once attempted.
        # If no multi-value methods succeed, each value is processed
        # independently with the remaining formats.
        for f in multi_formats:
            method = getattr(self, 'to_{0}'.format(f), None)

            # This formatter does not support this format, remove it
            # from the available list.
            if not method:
                continue

            if getattr(method, 'process_multiple', False):
                try:
                    output = method(values,
                                    fields=self.fields,
                                    concept=self.concept,
                                    process_multiple=True,
                                    **context)

                    if not isinstance(output, dict):
                        return OrderedDict([(self.concept.name, output)])

                    return output

                except Exception:
                    if self.concept and self.concept not in self._errors:
                        self._errors.add(self.concept)
                        log.exception('Multi-value formatter error')

        # The output is independent of the input. Formatters may output more
        # or less values than what was entered.
        output = OrderedDict()

        # Process each field and corresponding value separately.
        for i, (key, value) in enumerate(values.iteritems()):
            field = self.fields[key] if self.fields else None

            field_formats = list(preferred_formats)

            # Add field type if defined
            if field:
                if field.type:
                    field_formats.append(field.type)

                field_formats.append(field.simple_type)

            # Fallback to simple type (e.g. number) and finally 'raw'
            field_formats.append('raw')

            for f in field_formats:
                method = getattr(self, 'to_{0}'.format(f), None)

                if not method:
                    continue

                try:
                    value = method(value,
                                   field=field,
                                   concept=self.concept,
                                   process_multiple=False,
                                   **context)

                    # Add/update output and break loop
                    if isinstance(value, dict):
                        output.update(value)
                    else:
                        output[key] = value

                    break
                except Exception:
                    if field and field not in self._errors:
                        self._errors.add(field)
                        log.exception('Single-value formatter error')

        return output

    def __contains__(self, choice):
        return hasattr(self, 'to_{0}'.format(choice))

    def __unicode__(self):
        return u'{0}'.format(self.name or self.__class__.__name__)

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

        raise FormatterException(u'Cannot convert {0} to boolean'
                                 .format(value))

    def to_number(self, value, **context):
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

        raise FormatterException(u'Cannot convert {0} to number'.format(value))

    def to_coded(self, value, **context):
        # Attempts to convert value to its coded representation
        field = context.get('field')

        if field:
            for key, coded in field.coded_values:
                if key == value:
                    return coded

        raise FormatterException(u'No coded value for {0}'.format(value))

    def to_raw(self, value, **context):
        return value


class RawFormatter(Formatter):
    def __call__(self, values, *args, **kwargs):
        return super(RawFormatter, self).__call__(values, ['raw'])


registry = loader.Registry(default=Formatter, register_instance=False)
loader.autodiscover('formatters')

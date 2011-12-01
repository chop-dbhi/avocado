from copy import deepcopy

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.utils.encoding import force_unicode
from avocado.utils import loader
from avocado.conf import settings

DATA_CHOICES_MAP = settings.DATA_CHOICES_MAP

class Formatter(object):
    """Provides support for the core data formats with sensible defaults
    for handling converting Python datatypes to their formatted equivalent.

    Each core format method must return one of the following:
        Single formatted Value
        OrderedDict/sequence of key-value pairs

        If ta format method is unable to do either of these for the given
        value a FormatException must be raised.

        ``values`` - an OrderedDict containing each value along with the field
        instance it represents.

        ::

            values = OrderedDict({
                'first_name': {
                    'name': 'First Name',
                    'value': 'Bob',
                    'field': <Field "First Name">),
                },
                'last_name': {
                    'name': 'Last Name',
                    'value': 'Smith',
                    'field': <Field "Last Name">),
                },
            })

    """
    name = ''

    def __call__(self, values, concept, preferred_formats=None, **context):
        preferred_formats = list(preferred_formats) + ['raw']

        if not values:
            raise ValueError('No values supplied')

        output = deepcopy(values)

        # Iterate over all preferred formats and attempt to process the values.
        # For formatter methods that process all values must be tracked and
        # attempted only once. They are removed from the list once attempted.
        # If no preferred multi-value methods succeed, each value is processed
        # independently with the remaining formats
        for f in iter(preferred_formats):
            method = getattr(self, 'to_{0}'.format(f), None)
            # This formatter does not support this format, remove it
            # from the available list
            if not method:
                preferred_formats.pop(0)
                continue

            # The implicit behavior when handling multiple values is to process
            # them independently since, in most cases, they are not dependent on
            # on one another, but rather should be represented together since the
            # data is related. A formatter method can be flagged to process all values
            # together by setting the attribute ``process_multiple=True``. we must
            # check to if that flag has been set and simply pass through the values
            # and context to the method as is. if ``process_multiple`` is not set,
            # each value is handled independently
            if getattr(method, 'process_multiple', False):
                try:
                    self.process_multiple(method, output, concept, **context)
                    break
                # Remove from the preferred formats list since it failed
                except Exception:
                    preferred_formats.pop(0)

        # Attempt to process each 
        for key, data in output.iteritems():
            for f in preferred_formats:
                method = getattr(self, 'to_{0}'.format(f))
                try:
                    self.process_single(method, data, concept, **context)
                    break
                except:
                    pass
        return output

    def __contains__(self, choice):
        return hasattr(self, 'to_%s' % choice)

    def __unicode__(self):
        return u'%s' % self.name

    def process_single(self, method, data, concept, **context):
        name = data['name']
        value = data['value']
        field = data['field']

        fdata = method(name, value, field, concept, **context)

        if type(fdata) is dict:
            data.update(fdata)
        # assume single value
        else:
            data['value'] = fdata
        return data

    def process_multiple(self, method, values, concept, **context):
        # The output of a method that process multiple values
        # must return an OrderedDict or a sequence of key-value
        # pairs that can be used to create an OrderedDict
        fdata = method(values, concept, **context)

        if not isinstance(fdata, OrderedDict):
            values.update(fdata)
        else:
            values = fdata
        return values

    def to_string(self, name, value, field, concept, **context):
        # attempt to coerce non-strings to strings. depending on the data
        # types that are being passed into this, this may not be good
        # enough for certain datatypes or complext data structures
        if value is None:
            return u''
        return force_unicode(value, strings_only=False)

    def to_bool(self, name, value, field, concept, **context):
        # if value is native True or False value, return it
        # Change value to bool if value is a string of false or true
        if type(value) is bool:
            return value
        if value in ('true', 'True', '1', 1):
            return True
        if value in ('false', 'False', '0', 0):
            return False
        raise Exception('Cannot convert {0} to boolean'.format(value))

    def to_number(self, name, value, field, concept, **context):
        # attempts to convert a number. Starting with ints and floats
        # Eventually create to_decimal using the decimal library.
        if type(value) is int or type(value) is float:
            return value
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = float(value)
        return value

    def to_coded(self, name, value, field, concept, **context):
        # attempts to convert value to its coded representation
        return field.coded_values[value]

    def to_raw(self, name, value, field, concept, **context):
        return value


# initialize the registry that will contain all classes for this type of
# registry
registry = loader.Registry(default=Formatter)

# this will be invoked when it is imported by models.py to use the
# registry choices
loader.autodiscover('formatters')

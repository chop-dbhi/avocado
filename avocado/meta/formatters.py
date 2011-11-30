from collections import OrderedDict
from django.utils.encoding import force_unicode
from avocado.utils import loader

def noop(k, v, d, c, **x): return v

class Formatter(object):
    """Provides support for the core data formats with sensible defaults
    for handling converting Python datatypes to their formatted equivalent.

        ``values`` - an OrderedDict containing each value along with the field
        instance it represents.

        ::

            values = OrderedDict({
                'first_name': {
                    'name': 'First Name',
                    'value': 'Bob',
                    'definition': <Field "First Name">),
                },
                'last_name': {
                    'name': 'Last Name',
                    'value': 'Smith',
                    'definition': <Field "Last Name">),
                },
            })

    """
    name = ''

    def __call__(self, values, concept, choice=None, **context):
        if len(values) == 0:
            raise ValueError, 'no values supplied'

        if choice and choice not in self:
            raise AttributeError, 'the "%s" formatter is not supported' % choice

        out = values.copy()

        method = getattr(self, 'to_%s' % choice, noop)

        # the implicit behavior when handling multiple values is to process
        # them independently since, in most cases, they are not dependent on
        # on one another, but rather should be represented together since the
        # data is related. a formatter can be flagged to process all values
        # together by setting the attribute ``process_multiple=True``. we must
        # check to if that flag has been set and simply pass through the values
        # and context to the method as is. if ``process_multiple`` is not set,
        # each value is handled independently
        if getattr(method, 'process_multiple', False):
            data = method(values, concept, **context)

            # the output of a method that processes multiple values at once
            # must return an OrderedDict or a sequence of key-value pairs
            # that can be used to create an OrderedDict.
            if not isinstance(data, OrderedDict):
                out.update(data)
            else:
                out = data
        else:
            for key, data in values.iteritems():
                name = data['name']
                value = data['value']
                definition = data['definition']

                fdd = data.copy()
                fdata = method(name, value, definition, concept, **context)

                if type(fdata) is dict:
                    fdd.update(fdata)
                # assume single value 
                else:
                    fdd['value'] = fdata

                out[key] = fdd

        return out

    def __contains__(self, choice):
        return hasattr(self, 'to_%s' % choice)

    def __unicode__(self):
        return u'%s' % self.name

    def to_string(self, name, value, definition, concept, **context):
        # attempt to coerce non-strings to strings. depending on the data
        # types that are being passed into this, this may not be good
        # enough for certain datatypes or complext data structures
        if value is None:
            return u''
        return force_unicode(value, strings_only=False)

    to_string.none = u''

    def to_html(self, values, concept, **context):
        new_values = []

        for key, data in values.iteritems():
            name = data['name']
            value = data['value']
            definition = data['definition']

            # representing None is HTML needs to be distinct, so we include a
            # special style for it
            if value is None:
                tok = self.none

            # convert bools to their yes/no equivalents 
            elif type(value) is bool:
                tok = 'yes' if value else 'no'

            else:
                tok = self.to_string(name, value, definition, concept, **context)

            new_values.append(tok)

        return OrderedDict({'name': {'name': concept.name,
            'value': ' '.join(new_values), 'definition': definition}})

    to_html.none = '<span class="no-data">{no data}</span>'

    # this is a sensible default since HTML focuses more on "marking up" the
    # values with some semantic and/or visual relationship. since HTML has no
    # notion of a data structure, all values should usually be processed
    # together
    to_html.process_multiple = True


# initialize the registry that will contain all classes for this type of
# registry
registry = loader.Registry(default=Formatter)

# this will be invoked when it is imported by models.py to use the
# registry choices
loader.autodiscover('formatters')

.. include:: <isonum.txt>

Avocado Settings
================

INTERNAL_DATATYPE_MAP
---------------------
Default::

    {
        'auto': 'number',
        'biginteger': 'number',
        'boolean': 'boolean',
        'char': 'string',
        'date': 'date',
        'datetime': 'datetime',
        'decimal': 'number',
        'email': 'string',
        'file': 'string',
        'filepath': 'string',
        'float': 'number',
        'image': 'string',
        'integer': 'number',
        'ipaddress': 'string',
        'nullboolean': 'boolean',
        'positiveinteger': 'number',
        'positivesmallinteger': 'number',
        'slug': 'string',
        'smallinteger': 'number',
        'text': 'string',
        'time': 'time',
        'url': 'string',
    }

A mapping between model field internal datatypes and sensible client-friendly
datatypes. In virtually all cases, client programs only need to differentiate
between high-level types like number, string, and boolean. Finer separation may
be desired to alter the allowed operators or may infer a different client-side
representation.

The internal datatypes map one-to-one to the available `model field types`_.

.. _`model field types`: http://docs.djangoproject.com/en/1.3/ref/models/fields/#field-types


DATATYPE_OPERATOR_MAP
---------------------
Default::

    {
        'boolean': ('exact', '-exact'),
        'date': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
        'datetime': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
        'number': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
        'string': ('iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'),
        'time': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    }

A mapping between the client-friendly datatypes, defined in 
INTERNAL_DATATYPE_MAP_, and sensible operators that will be used to validate
a query condition of the given type. In many cases, these types support more
operators than what are defined, but are not included because they are not
commonly used.

The available operators are a subset of the `field lookups`_ Django provides.
See the list of available :doc:`operators`.

.. _`field lookups`: http://docs.djangoproject.com/en/1.3/ref/models/querysets/#field-lookups


DATA_CHOICES_MAP
----------------
Default::

    {
        False: 'No',
        True: 'Yes',
        None: 'No Data',
    }

Contains a mapping from Python values to a corresponding human readable
representation. This will only ever be applicable when values are being
presented to clients as a list of choices when ``Field.enable_choices``
is ``True``.


INTERNAL_DATATYPE_FORMFIELDS
----------------------------
Default::

    {
        'auto': 'IntegerField',
        'integer': 'FloatField',
        'positiveinteger': 'FloatField',
        'positivesmallinteger': 'FloatField',
        'smallinteger': 'FloatField',
    }

A general mapping of form field class overrides for any model field types. The
mapping is similar to the INTERNAL_DATATYPE_MAP_, but the values reference
internal formfield classes, that is, ``integer`` |rarr| ``FloatField``. In many
cases, the validation performed can be less restrictive for read-only SQL queries
than what is actually required by databases for queries that will write
to the database.

Any value in this mapping that is a path (``.``-separated) are assumed to be
custom form field classes, e.g::

    ...
    'integer': 'myapp.formfields.SpecialInteger',
    ...

Otherwise, they are assumed to be one of Django's built-in form field classes.

.. note::

    As you can see in the default overrides above, allowing float values where
    integers are typically required is common and has no side effects from a
    database standpoint. Thus these overrides were chosen to be the default
    overrides.


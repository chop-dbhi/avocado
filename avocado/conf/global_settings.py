# A mapping between model field internal datatypes and sensible
# client-friendly datatypes. In virtually all cases, client programs
# only need to differentiate between high-level types like number, string,
# and boolean. More granular separation be may desired to alter the
# allowed operators or may infer a different client-side representation
SIMPLE_TYPE_MAP = {
    'auto': 'number',
    'biginteger': 'number',
    'decimal': 'number',
    'float': 'number',
    'integer': 'number',
    'positiveinteger': 'number',
    'positivesmallinteger': 'number',
    'smallinteger': 'number',

    'nullboolean': 'boolean',

    'char': 'string',
    'email': 'string',
    'file': 'string',
    'filepath': 'string',
    'image': 'string',
    'ipaddress': 'string',
    'slug': 'string',
    'text': 'string',
    'url': 'string',
}

# A mapping between the client-friendly datatypes and sensible operators
# that will be used to validate a query condition. In many cases, these types
# support more operators than what are defined, but are not include because
# they are not commonly used.
OPERATOR_MAP = {
    'boolean': ('exact', '-exact', 'in', '-in'),
    'date': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'number': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'string': ('exact', '-exact', 'iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'),
    'datetime': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'time': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
}

# Contains a mapping from raw data values to a corresponding human
# readable representation. this will only ever be applicable when values
# are being presented to client programs as potential choices
RAW_DATA_MAP = {
    None: 'Null',
    '': '(empty string)',
}

# A general mapping of formfield overrides for all subclasses. the mapping is
# similar to the SIMPLE_TYPE_MAP, but the values reference internal
# formfield classes, that is integer -> IntegerField. in many cases, the
# validation performed may need to be a bit less restrictive than what the
# is actually necessary
INTERNAL_DATATYPE_FORMFIELDS = {
    'auto': 'IntegerField',
    'integer': 'FloatField',
    'positiveinteger': 'FloatField',
    'positivesmallinteger': 'FloatField',
    'smallinteger': 'FloatField',

    # Generic datatypes mapped from above
    'number': 'FloatField',
}

# The minimum number of distinct values required when determining to set the
# `searchable` flag on `DataField` instances during the `sync` process. This
# will only be applied to fields with a Avocado datatype of 'string'
SYNC_ENUMERABLE_MAXIMUM = 30

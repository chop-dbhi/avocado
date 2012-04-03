# A mapping between model field internal datatypes and sensible
# client-friendly datatypes. in virtually all cases, client programs
# only need to differentiate between high-level types like number,
# string, and boolean. finer separation be may desired to alter the
# allowed operators or may infer a different client-side representation
INTERNAL_DATATYPE_MAP = {
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

# A mapping between the client-friendly datatypes and sensible operators
# that will be used to validate a query condition. in many cases, these types
# support more operators than what are defined, but are not include because
# they are not commonly used
DATATYPE_OPERATOR_MAP = {
    'boolean': ('exact', '-exact'),
    'date': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'datetime': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'number': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'string': ('exact', '-exact', 'iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'),
    'time': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
}

# Contains a mapping from raw data values to a corresponding human
# readable representation. this will only ever be applicable when values
# are being presented to client programs as potential choices
DATA_CHOICES_MAP = {
#    False: 'No',
#    True: 'Yes',
    None: 'Null',
}

# A general mapping of formfield overrides for all subclasses. the mapping is
# similar to the INTERNAL_DATATYPE_MAP, but the values reference internal
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


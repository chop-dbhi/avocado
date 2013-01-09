# A mapping between model field internal datatypes and sensible
# client-friendly datatypes. In virtually all cases, client programs
# only need to differentiate between high-level types like number, string,
# and boolean. More granular separation be may desired to alter the
# allowed operators or may infer a different client-side representation
SIMPLE_TYPE_MAP = {
    'auto': 'key',
    'foreignkey': 'key',

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
    'key': ('exact', '-exact', 'in', '-in'),
    'boolean': ('exact', '-exact', 'in', '-in'),
    'date': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'number': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'string': ('exact', '-exact', 'iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'),
    'datetime': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'time': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
}

# A general mapping of formfield overrides for all subclasses. the mapping is
# similar to the SIMPLE_TYPE_MAP, but the values reference internal
# formfield classes, that is integer -> IntegerField. in many cases, the
# validation performed may need to be a bit less restrictive than what the
# is actually necessary
INTERNAL_DATATYPE_FORMFIELDS = {
    'integer': 'FloatField',
    'positiveinteger': 'FloatField',
    'positivesmallinteger': 'FloatField',
    'smallinteger': 'FloatField',

    # Generic datatypes mapped from above
    'number': 'FloatField',
}

# The minimum number of distinct values required when determining to set the
# `searchable` flag on `DataField` instances during the `init` process. This
# will only be applied to fields with a Avocado datatype of 'string'
ENUMERABLE_MAXIMUM = 30

# Flag for enabling the history API
HISTORY_ENABLED = False

# The maximum size of a user's history. If the value is an integer, this
# is the maximum number of allowed items in the user's history. Set to
# `None` (or 0) to enable unlimited history. Note, in order to enforce this
# limit, the `avocado history --prune` command must be executed to remove
# the oldest history from each user based on this value.
HISTORY_MAX_SIZE = None

# App that the metadata migrations will be created for. This is typically the
# project itself.
METADATA_MIGRATION_APP = None

# Directory for the migration backup fixtures. If None, this will default to
# the fixtures dir in the app defined by `METADATA_MIGRATION_APP`
METADATA_FIXTURE_DIR = None

METADATA_FIXTURE_SUFFIX = 'avocado_metadata'

METADATA_MIGRATION_SUFFIX = 'avocado_metadata_migration'

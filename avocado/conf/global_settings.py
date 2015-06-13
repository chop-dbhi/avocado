# A mapping between model field internal datatypes and sensible
# client-friendly datatypes. In virtually all cases, client programs
# only need to differentiate between high-level types like number, string,
# and boolean. More granular separation be may desired to alter the
# allowed operators or may infer a different client-side representation
SIMPLE_TYPES = {
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
OPERATORS = {
    'key': ('exact', '-exact', 'in', '-in'),
    'boolean': ('exact', '-exact', 'in', '-in'),
    'date': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte',
             'range', '-range'),
    'number': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte',
               'range', '-range'),
    'string': ('exact', '-exact', 'iexact', '-iexact', 'in', '-in',
               'icontains', '-icontains', 'iregex', '-iregex'),
    'datetime': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte',
                 'range', '-range'),
    'time': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte',
             'range', '-range'),
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
    'biginteger': 'FloatField',
}

# The minimum number of distinct values required when determining to set the
# `searchable` flag on `DataField` instances during the `init` process. This
# will only be applied to fields with a Avocado datatype of 'string'
ENUMERABLE_MAXIMUM = 30

# Flag for enabling the history API
HISTORY_ENABLED = True

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

# Query processors
QUERY_PROCESSORS = {
    'default': 'avocado.query.pipeline.QueryProcessor',
}

# Custom validation error and warnings messages
VALIDATION_ERRORS = {}
VALIDATION_WARNINGS = {}

# Toggle whether DataField instances should cache the underlying data
# for their most common data access methods.
DATA_CACHE_ENABLED = True

# These settings affect how queries can be shared between users.
# A user is able to enter either a username or an email of another user
# they wish to share the query with. To limit to only one type of sharing
# set the appropriate setting to True and all others to false.
SHARE_BY_USERNAME = True
SHARE_BY_EMAIL = True
SHARE_BY_USERNAME_CASE_SENSITIVE = True

# Toggle whether the permissions system should be enabled.
# If django-guardian is installed and this value is None or True, permissions
# will be applied. If the value is True and django-guardian is not installed
# it is an error. If set to False the permissions will not be applied.
PERMISSIONS_ENABLED = None

# Caches are used to improve performance across various APIs. The two primary
# ones are data and query. Data cache is used for individual data field
# caching such as counts, values, and aggregations. Query cache is used for
# the ad-hoc queries built from a context and view.
DATA_CACHE = 'default'
QUERY_CACHE = 'default'

# Name of the queue to use for scheduling and working on async jobs.
ASYNC_QUEUE = 'avocado'

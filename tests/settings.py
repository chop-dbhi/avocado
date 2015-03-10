import os
import sys
import getpass


ENGINES = ('sqlite', 'postgres', 'mysql')


ENABLE_SQLITE = os.environ.get('ENABLE_SQLITE', '1')
ENABLE_POSTGRES = os.environ.get('ENABLE_POSTGRES', '0')
ENABLE_MYSQL = os.environ.get('ENABLE_MYSQL', '0')
DEFAULT_ENGINE = os.environ.get('DEFAULT_ENGINE')

POSTGRES_TEST_NAME = os.environ.get('POSTGRES_TEST_NAME', 'avocado')
POSTGRES_TEST_USER = os.environ.get('POSTGRES_TEST_USER', getpass.getuser())
POSTGRES_TEST_PASSWORD = os.environ.get('POSTGRES_TEST_PASSWORD')

MYSQL_TEST_NAME = os.environ.get('MYSQL_TEST_NAME', 'avocado')
MYSQL_TEST_USER = os.environ.get('MYSQL_TEST_USER', getpass.getuser())
MYSQL_TEST_PASSWORD = os.environ.get('MYSQL_TEST_PASSWORD')

DATABASES = {}


if ENABLE_SQLITE == '1':
    DATABASES['sqlite'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'tests.db'),
        # Explicitly set the test name otherwise Django will use an in-memory
        # database.
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'tests.db'),
    }

if ENABLE_POSTGRES == '1':
    DATABASES['postgres'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': POSTGRES_TEST_NAME,
        'USER': POSTGRES_TEST_USER,
        'PASSWORD': POSTGRES_TEST_PASSWORD,
    }

if ENABLE_MYSQL == '1':
    DATABASES['mysql'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_TEST_NAME,
        'USER': MYSQL_TEST_USER,
        'PASSWORD': MYSQL_TEST_PASSWORD,
    }


# Ensure the selected default engine is enabled. If not selected use the only
# database present or sqlite otherwise.
if DEFAULT_ENGINE:
    if DEFAULT_ENGINE not in DATABASES:
        print('The selected default engine not enabled.')
        sys.exit(1)
else:
    if len(DATABASES) == 1:
        DEFAULT_ENGINE = tuple(DATABASES.keys())[0]
    elif 'sqlite' not in DATABASES:
        print('A default engine must specified.')
        sys.exit(1)
    else:
        DEFAULT_ENGINE = 'sqlite'

DATABASES['default'] = DATABASES[DEFAULT_ENGINE]


INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'haystack',
    'guardian',
)

import django
if django.VERSION < (1, 7):
    INSTALLED_APPS += ('south',)

INSTALLED_APPS += (
    'avocado',
    'avocado.events',

    'tests',
    'tests.cases.core',
    'tests.cases.exporting',
    'tests.cases.formatters',
    'tests.cases.events_test',
    'tests.cases.history',
    'tests.cases.models',
    'tests.cases.query',
    'tests.cases.search',
    'tests.cases.stats',
    'tests.cases.subcommands',
    'tests.cases.validation',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SITE_ID = 1

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh.index'),
    }
}

ANONYMOUS_USER_ID = -1

TEST_RUNNER = 'tests.runner.ProfilingTestRunner'
TEST_PROFILE = 'unittest.profile'

LOGGING = {
    'version': 1,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'avocado': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

SOUTH_TESTS_MIGRATE = False

AVOCADO = {
    'HISTORY_ENABLED': False,
    'HISTORY_MAX_SIZE': 50,
    'METADATA_MIGRATION_APP': 'core',
    'DATA_CACHE_ENABLED': False,
}

MODELTREES = {
    'default': {
        'model': 'tests.Employee',
    },
    'title': {
        'model': 'tests.Title',
    },
    'office': {
        'model': 'tests.Office',
    }
}

SECRET_KEY = 'acb123'

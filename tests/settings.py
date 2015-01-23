import os
import getpass

POSTGRES_TEST_NAME = os.environ.get('POSTGRES_TEST_NAME', 'avocado')
POSTGRES_TEST_USER = os.environ.get('POSTGRES_TEST_USER', getpass.getuser())
POSTGRES_TEST_PASSWORD = os.environ.get('POSTGRES_TEST_PASSWORD')

MYSQL_TEST_NAME = os.environ.get('MYSQL_TEST_NAME', 'avocado')
MYSQL_TEST_USER = os.environ.get('MYSQL_TEST_USER', getpass.getuser())
MYSQL_TEST_PASSWORD = os.environ.get('MYSQL_TEST_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'tests.db'),
        # Explicitly set the test name otherwise Django will use an in-memory
        # database.
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'tests.db'),
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': POSTGRES_TEST_NAME,
        'USER': POSTGRES_TEST_USER,
        'PASSWORD': POSTGRES_TEST_PASSWORD,
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_TEST_NAME,
        'USER': MYSQL_TEST_USER,
        'PASSWORD': MYSQL_TEST_PASSWORD,
    },
}

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'haystack',
    'guardian',
    'south',

    'avocado',

    'tests',
    'tests.cases.core',
    'tests.cases.exporting',
    'tests.cases.formatters',
    'tests.cases.events',
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

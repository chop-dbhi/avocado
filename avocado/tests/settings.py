import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

MODELTREES = {
    'default': {
        'model': 'tests.Employee'
    }
}

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'haystack',
    'guardian',
    'avocado',
    'avocado.coded',
    'avocado.stats',
    'avocado.tests',
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
        'PATH': os.path.join(os.path.dirname(__file__), '../../../whoosh.index'),
    }
}

ANONYMOUS_USER_ID = -1

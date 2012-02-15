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
    'avocado',
    'avocado.tests',
)

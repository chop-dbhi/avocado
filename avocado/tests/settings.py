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
    'avocado.meta',
    'avocado.tests',
)

COVERAGE_MODULES = (
    'avocado.meta.formatters',
    'avocado.meta.exporters._base',
    'avocado.meta.exporters._csv',
    'avocado.meta.exporters._excel',
    'avocado.meta.exporters._sas',
    'avocado.meta.exporters._r',
    'avocado.meta.exporters._json',
#    'avocado.meta.logictree',
    'avocado.meta.managers',
    'avocado.meta.mixins',
    'avocado.meta.models',
    'avocado.meta.operators',
    'avocado.meta.translators',
    'avocado.meta.utils',
)

TEST_RUNNER = 'avocado.tests.coverage_test.CoverageTestRunner'

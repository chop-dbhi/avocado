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

COVERAGE_MODULES = (
    'avocado.formatters',
    'avocado.exporters._base',
    'avocado.exporters._csv',
    'avocado.exporters._excel',
    'avocado.exporters._sas',
    'avocado.exporters._r',
    'avocado.exporters._json',
#    'avocado.logictree',
    'avocado.managers',
    'avocado.models',
    'avocado.operators',
    'avocado.translators',
    'avocado.core.binning',
    'avocado.core.mixins',
    'avocado.core.managers',
    'avocado.core.loader',
)

TEST_RUNNER = 'avocado.tests.coverage_test.CoverageTestRunner'

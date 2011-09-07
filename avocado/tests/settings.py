MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'avocado.store.middleware.SessionReportMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'serrano.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'restlib',
    'avocado',
    'avocado.tests',
)

COVERAGE_MODULES = (
    'avocado.store.forms.context',
    'avocado.store.forms.scope',
    'avocado.store.forms.perspective',
    'avocado.store.forms.report',
)

TEST_RUNNER = 'avocado.tests.coverage_test.CoverageTestRunner'

AVOCADO_SETTINGS = {
    'MODELTREES': {
        'default': {
            'root_model': 'avocado.Category',
        }
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'avocado.db',
    }
}

INSTALLED_APPS = (
    'avocado',
    'avocado.tests',
)

AVOCADO_SETTINGS = {
    'MODELTREES': {
        'default': {
            'root_model': 'avocado.Category',
        }
    },
}

class Settings(object):
    DEFAULT_SETTINGS = {
        'ENABLE_GROUP_PERMISSIONS': False,

        'FORMATTER_TYPES': {},
        'FORMATTER_FIELD_SUFFIX': '%s_fmt',
        'FORMATTER_MODULE_NAME': 'format',

        'VIEW_MODULE_NAME': 'viewset',

        'TRANSLATOR_MODULE_NAME': 'translate',

        'MODELTREE_CONF': None,

        'DEFAULT_COLUMN_ORDERING': None,
        'DEFAULT_COLUMNS': None,
    }

    def __init__(self, user_settings={}):
        for key, value in self.DEFAULT_SETTINGS.items():
            if key.upper() in user_settings:
                value = user_settings[key]
            setattr(self, key, value)


try:
    from django.conf import settings as base_settings
    settings = Settings(getattr(base_settings, 'AVOCADO_SETTINGS', {}))
except ImportError:
    settings = Settings()

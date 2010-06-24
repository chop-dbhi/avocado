from django.db import models

class Settings(object):
    DEFAULT_SETTINGS = {
        'ENABLE_GROUP_PERMISSIONS': False,
        'COLUMN_CONCEPT_MIXIN': models.Model,
        'CRITERION_CONCEPT_MIXIN': models.Model,
        'FORMATTER_TYPES': {},
        'VIEW_TYPES': {},
    }

    def __init__(self, user_settings={}):
        for key, value in self.DEFAULT_SETTINGS.items():
            if key.upper() in user_settings:
                value = user_settings[key]
            setattr(self, key, value)


try:
    from django.conf.settings import AVOCADO_SETTINGS
    settings = Settings(AVOCADO_SETTINGS)
except ImportError:
    settings = Settings()
    

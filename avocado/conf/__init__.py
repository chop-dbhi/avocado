from django.utils.functional import LazyObject
from django.conf import settings as django_settings
from avocado.conf import global_settings


class Settings(object):
    def __init__(self, settings_dict):
        # set the initial settings as defined in the global_settings
        for setting in iter(dir(global_settings)):
            if setting == setting.upper():
                setattr(self, setting, getattr(global_settings, setting))

        # iterate over the user-defined settings and override the default
        # settings
        for key, value in iter(settings_dict.items()):
            if key == key.upper():
                setattr(self, key, value)


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(getattr(django_settings, 'AVOCADO', {}))


settings = LazySettings()

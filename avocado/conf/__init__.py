from django.utils.functional import LazyObject
from django.conf import settings as default_settings

from avocado.conf import global_settings

class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(getattr(default_settings, 'AVOCADO_SETTINGS', {}))


class Settings(object):
    def __init__(self, settings_dict):
        for setting in dir(global_settings):
            if setting == setting.upper():
                setattr(self, setting, getattr(global_settings, setting))

        for k, v in settings_dict.items():
            if k == k.upper():
                setattr(self, k, v)

settings = LazySettings()

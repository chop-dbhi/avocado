import functools
from django.core.exceptions import ImproperlyConfigured
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


# Keep track of the officially supported apps and libraries used for various
# features.
INSTALLED_LIBS = {
    'django.contrib.sites': False,
    'haystack': False,
    'numpy': False,
    'scipy': False,
    'actstream': False,
    'openpyxl': False,
}

# Support for django sites framework
if 'django.contrib.sites' in django_settings.INSTALLED_APPS:
    INSTALLED_LIBS['django.contrib.sites'] = True

# Full-text search engine
try:
    import haystack
    INSTALLED_LIBS['haystack'] = True
except ImportError:
    pass

# High performance data structures
try:
    import numpy
    INSTALLED_LIBS['numpy'] = True
except ImportError:
    pass

# Statistical functions
try:
    import scipy
    INSTALLED_LIBS['scipy'] = True
except ImportError:
    pass

# Activity streams
try:
    import actstream
    if 'actstream' in django_settings.INSTALLED_APPS:
        INSTALLED_LIBS['acstream'] = True
except ImportError:
    pass

try:
    import openpyxl
    INSTALLED_LIBS['openpyxl'] = True
except ImportError:
    pass


def lib_required(lib):
    "Decorator for functions that require a supported third-party library."
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not INSTALLED_LIBS[lib]:
                raise ImproperlyConfigured('{0} must be installed to use this feature.'.format(lib))
            return f(*args, **kwargs)
        return wrapper
    return decorator

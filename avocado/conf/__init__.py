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
OPTIONAL_DEPS = {
    'haystack': False,
    'numpy': False,
    'scipy': False,
    'actstream': False,
    'openpyxl': False,
    'guardian': False,
}

# Full-text search engine
try:
    import haystack
    OPTIONAL_DEPS['haystack'] = True
except (ImportError, ImproperlyConfigured):
    pass

# High performance data structures
try:
    import numpy
    OPTIONAL_DEPS['numpy'] = True
except ImportError:
    pass

# Statistical functions
try:
    import scipy
    OPTIONAL_DEPS['scipy'] = True
except ImportError:
    pass

# Activity streams
try:
    import actstream
    if 'actstream' in django_settings.INSTALLED_APPS:
        OPTIONAL_DEPS['acstream'] = True
except ImportError:
    pass

# Native MS Excel reading/writing support
try:
    import openpyxl
    OPTIONAL_DEPS['openpyxl'] = True
except ImportError:
    pass

# Generic object-level permissions
try:
    import guardian
    OPTIONAL_DEPS['guardian'] = True
except ImportError:
    pass


def requires_dep(lib):
    "Decorator for functions that require a supported third-party library."
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not OPTIONAL_DEPS[lib]:
                raise ImproperlyConfigured('{0} must be installed to use this feature.'.format(lib))
            return f(*args, **kwargs)
        return wrapper
    return decorator

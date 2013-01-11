import re
import functools
from django.dispatch import receiver
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject
from django.conf import settings as django_settings
from django.test.signals import setting_changed
from avocado.conf import global_settings


class Settings(object):
    def __init__(self, settings_dict):
        # set the initial settings as defined in the global_settings
        for setting in iter(dir(global_settings)):
            setattr(self, setting, getattr(global_settings, setting))

        # iterate over the user-defined settings and override the default
        # settings
        for key, value in iter(settings_dict.items()):
            setattr(self, key, value)

    def __setattr__(self, key, value):
        if key == key.upper():
            default = getattr(self, key, None)
            if isinstance(default, dict):
                default.update(value)
            else:
                object.__setattr__(self, key, value)


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(getattr(django_settings, 'AVOCADO', {}))


settings = LazySettings()

@receiver(setting_changed)
def test_setting_changed_handler(**kwargs):
    if kwargs['setting'] == 'AVOCADO':
        for key, value in kwargs['value'].iteritems():
            setattr(settings._wrapped, key, value)
    elif kwargs['setting'].startswith('AVOCADO_'):
        key = kwargs['setting'][8:]
        value = kwargs['value']
        setattr(settings._wrapped, key, value)


class Dependency(object):
    name = ''

    def __nonzero__(self):
        return self.installed and self.setup

    def __unicode__(self):
        return self.name

    @property
    def doc(self):
        return re.sub('\n( )+', '\n', self.__doc__ or '').strip('\n')

    @property
    def marked_doc(self):
        try:
            import markdown
        except ImportError:
            return self.doc
        return markdown.markdown(self.doc)

    def test_install(self):
        raise NotImplemented

    def test_setup(self):
        return self.test_install()

    @property
    def installed(self):
        return self.test_install() is not False

    @property
    def setup(self):
        return self.test_setup() is not False


class Haystack(Dependency):
    """What's having all this great descriptive data if no one can find it?
    Haystack provides search engine facilities for the metadata.

    Install by doing `pip install django-haystack` and installing one of the
    supported search engine backends. The easiest to setup is Whoosh which is
    implemented in pure Python. Install it by doing `pip install whoosh`. Add
    haystack to `INSTALLED_APPS`.
    """

    name = 'haystack'

    # An import may cause an improperly configured error, so this catches
    # and returns the error for downstream use.
    def _test(self):
        try:
            import haystack
        except (ImportError, ImproperlyConfigured), e:
            return e

    def test_install(self):
        error = self._test()
        if isinstance(error, ImportError):
            return False

    def test_setup(self):
        error = self._test()
        if isinstance(error, ImproperlyConfigured):
            return False


#class Numpy(Dependency):
#    name = 'numpy'
#
#    def test_install(self):
#        try:
#            import numpy
#        except ImportError:
#            return False


class Scipy(Dependency):
    """Avocado comes with a stats package for performing some rudimentary
    statistical, aggregation and clustering operations on the data. This is not
    always required or necessary for all data, but if there is a heavy emphasis
    on numerical data or the amount of data is quite large, the stats may come
    in handy.

    Install by doing `pip install numpy` first (a dependency of SciPy), followed
    by `pip install scipy`. Note, there are a few dependencies for compilation,
    so review SciPy's [installation instructions](http://www.scipy.org/Installing_SciPy)
    for more details.
    """

    name = 'scipy'

    def test_install(self):
        try:
            import scipy
        except ImportError:
            return False


class Openpyxl(Dependency):
    """Avocado comes with an export package for supporting various means of
    exporting data into different formats. One of those formats is the native
    Microsoft Excel .xlsx format. To support that, the openpyxl library is used.

    Install by doing `pip install openpyxl`.
    """

    name = 'openpyxl'

    def test_install(self):
        try:
            import openpyxl
        except ImportError:
            return False


class Guardian(Dependency):
    """This enables fine-grain control over who has permissions for various
    DataFields. Permissions can be defined at a user or group level.

    Install by doing `pip install django-guardian` and adding guardian to
    `INSTALLED_APPS`.
    """

    name = 'guardian'

    def test_install(self):
        try:
            import guardian
        except ImportError:
            return False


# Keep track of the officially supported apps and libraries used for various
# features.
OPTIONAL_DEPS = {
    'haystack': Haystack(),
#    'numpy': Numpy(),
    'scipy': Scipy(),
    'openpyxl': Openpyxl(),
    'guardian': Guardian(),
}


def requires_dep(lib):
    "Decorator for functions that require a supported third-party library."
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            dep = OPTIONAL_DEPS[lib]
            if not dep:
                raise ImproperlyConfigured('{0} must be installed to use this feature.\n\n{1}'.format(lib, dep.__doc__))
            return f(*args, **kwargs)
        return wrapper
    return decorator

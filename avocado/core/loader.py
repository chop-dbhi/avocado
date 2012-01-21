from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Registry(object):
    "Simple class that keeps track of a set of registered classes."
    def __init__(self, default=None):
        self.default = default
        self._registry = {}

    def __getitem__(self, name):
        return self._registry.get(name, self.default)

    def register(self, klass, name=None):
        """Registers a class with an optional name. The class name will be used
        if not supplied.
        """
        name = name or klass.__name__
        if name in self._registry:
            raise AlreadyRegistered('The class %s is already registered' % name)

        # check to see if this class should be used as the default for this
        # registry
        if getattr(klass, 'default', False):
            # ensure the default if already overriden is not being overriden
            # again.
            if self.default:
                raise ImproperlyConfigured('The default class cannot be set '
                    'more than once for this registry (%s is the default).' %
                    self.default.__name__)

            self.default = klass
        else:
            if name in self._registry:
                raise AlreadyRegistered('Another class is registered with the '
                    'name "%s"' % name)

            self._registry[name] = klass

    def unregister(self, name):
        """Unregisters a class. Note that these calls must be made in
        INSTALLED_APPS listed after the apps that already registered the class.
        """
        if not isinstance(name, basestring):
            name = name.__name__
        if name not in self._registry:
            raise NotRegistered('No class is registered under the name "%s"' % name)
        self._registry.pop(name)

    @property
    def choices(self):
        "Returns a 2-tuple list of all registered class instance names."
        return sorted((x, x) for x in self._registry.iterkeys())


def autodiscover(module_name):
    """Simple auto-discover for looking through each INSTALLED_APPS for each
    ``module_name`` and fail silently when not found. This should be used for
    modules that have 'registration' like behavior.
    """
    for app in settings.INSTALLED_APPS:
        # Attempt to import the app's ``module_name``.
        try:
            import_module('%s.%s' % (app, module_name))
        except:
            pass

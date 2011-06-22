from django.conf import settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Registry(object):
    """Keeps track of registered classes along with named instances. Only one
    instance is created for a given class, so the instance should be stateless.
    """
    def __init__(self, default=None):
        # store first default
        self._default = default() if default else None

        self.default = self._default

        self._registry = {}
        self._objects = {}

    def __getitem__(self, name):
        return self._objects.get(name, self.default)

    def register(self, klass, name=None):
        """Registers a class with an optional name. The class name will be used
        if not supplied.
        """
        if klass in self._registry:
            raise AlreadyRegistered('The class %s is already registered' %
                klass.__name__)

        # check to see if this class should be used as the default for this
        # registry, warn
        if getattr(klass, 'default', False):

            # ensure the default if already overriden is not being overriden
            # again.
            if self.default and self.default is not self._default:
                raise ImproperlyConfigured('The default class cannot be set '
                    'more than once for this registry (%s was the default).' %
                    self.default.__class__.__name__)

            self.default = klass()
        else:
            if not name:
                name = klass.__name__

            if name in self._objects:
                raise AlreadyRegistered('Another class is registered with the '
                    'name "%s"' % name)

            self._registry[klass] = name
            self._objects[name] = klass()

    def unregister(self, klass):
        """Unregisters a class. Note that these calls must be made in
        INSTALLED_APPS listed after the apps that already registered the class.
        """
        if klass not in self._registry:
            raise NotRegistered('The class %s is not registered' %
                klass.__name__)
        name = self._registry.pop(klass)
        self._objects.pop(name)

    @property
    def choices(self):
        "Returns a 2-tuple list of all registered class instance names."
        return sorted((n, n) for n in self._registry.itervalues())


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

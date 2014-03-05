import inspect
from django.conf import settings
from django.utils.importlib import import_module


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Registry(object):
    "Registry for classes or instances."
    def __init__(self, default=None, name=None, register_instance=True):
        self.register_instance = register_instance
        self._registry = {}
        self.default = None

        # Register the default class/instance
        if default:
            self.register(default, name, default=True)

    def __len__(self):
        return len(self._registry)

    def __nonzero__(self):
        return True

    def __contains__(self, key):
        return key in self._registry

    def __getitem__(self, key):
        return self._registry.get(key, self.default)

    def get(self, name):
        if name in self:
            return self[name]
        return self.default

    def _register(self, obj, name=None, default=False):
        if default and not name:
            name = 'Default'

        if inspect.isclass(obj):
            name = name or obj.__name__
            # Create an instance if instances should be registered
            if self.register_instance:
                obj = obj()
        else:
            name = name or obj.__class__.__name__

        if default:
            self.default = self._registry[name] = obj
        elif name in self._registry:
            raise AlreadyRegistered(u'The object "{0}" is already '
                                    'registered'.format(name))
        self._registry[name] = obj

    def register(self, obj, name=None, default=False):
        """Registers a class or instance with an optional name. The class
        name will be used if not supplied. This method can be used as a
        decorator:

            @loader.register
            class MyClass(object):
                pass

        or:

            @loader.register('My Class', default=True)
            class MyClass(object):
                pass
        """

        # No reliable way to check for registered class/instance, so
        # the first non-required argument is checked for. If this is
        # the case, shift the arguments
        if isinstance(obj, (str, unicode)):
            default, name = name, obj

            def func(obj, name=name, default=default):
                self._register(obj, name, default)

            return func

        self._register(obj, name, default)

    def unregister(self, name):
        """Unregisters an object.

        **Note:** that these calls must be made in INSTALLED_APPS listed
        after the apps that already registered the class.
        """
        # Use the name of the class if passed in. Second condition checks
        # for an instance of the class.
        if inspect.isclass(name):
            name = name.__name__
        elif hasattr(name, '__class__'):
            name = name.__class__.__name__

        if name not in self._registry:
            raise NotRegistered(u'No object "{0}" registered'.format(name))
        self._registry.pop(name)

    @property
    def choices(self):
        "Returns a 2-tuple list of all registered class instance names."
        return sorted((x, x) for x in self._registry.iterkeys())


def autodiscover(module_name):
    """Simple auto-discover for looking through each INSTALLED_APPS for each
    module_name and fail silently when not found or if an error occurs.
    """
    for app in settings.INSTALLED_APPS:
        # Attempt to import the app's ``module_name``.
        try:
            import_module('{0}.{1}'.format(app, module_name))
        except:
            pass

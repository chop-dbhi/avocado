import imp

from django.conf import settings
from django.utils.importlib import import_module

from avocado.exceptions import RegisterError, AlreadyRegisteredError
from avocado.utils.camel import uncamel

class BaseLibrary(object):
    STORE_KEY = ''
    DISCOVER_MODE = False

    def __init__(self):
        self._cache = {}

    def _add_store(self):
        for key in self._cache:
            self._cache[key][self.STORE_KEY] = {}        

    def _format_name(self, name, suffix=''):
        if suffix and name.endswith(suffix):
            name = name[:-len(suffix)]
        return uncamel(name)

    def _get_store(self, key):
        return self._cache[key][self.STORE_KEY]

    def _get_class_name(self, klass):
        if hasattr(klass, 'name'):
            return klass.name
        return self._format_name(klass.__name__)

    def _add_item(self, key, klass_name, obj, errmsg=''):
        store = self._get_store(key)

        # if already registered under the same name, test if the classes are
        # the same -- replace if true, throw error if not
        if store.has_key(klass_name):
            robj = store.get(klass_name)
            if obj.__class__ is not robj.__class__:
                raise AlreadyRegisteredError, errmsg
        store.update({klass_name: obj})

    def _pre_register(self, klass, superclass):
        "Test class being registered is valid."
        if not issubclass(klass, superclass):
            raise RegisterError, '%s must be a subclass of %s' % (repr(klass),
                superclass.__name__)

    def _register(self, klass_name, obj):
        raise NotImplementedError, 'Subclasses must implement this method'

    def register(self, klass, superclass=object):
        self._pre_register(klass, superclass)

        class_name = self._get_class_name(klass)
        obj = klass()

        self._register(class_name, obj)
        return klass

    def choices(self, key):
        "Returns a list of tuples that can be used as choices in a form."
        store = self._get_store(key)
        choices = []
        for name in store.keys():
            choices.append((name, name))
        return choices

    def get(self, key, name):
        "Retrieve the cached instance given the name it is registered under."
        return self._get_store(key).get(name, None)

    def autodiscover(self, mod_name):
        if self.DISCOVER_MODE:
            return

        self.DISCOVER_MODE = True

        for app in settings.INSTALLED_APPS:
            try:
                app_path = import_module(app).__path__
            except AttributeError:
                continue
            try:
                imp.find_module(mod_name, app_path)
            except ImportError:
                continue

            import_module('%s.%s' % (app, mod_name))

        self.DISCOVER_MODE = False

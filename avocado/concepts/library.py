import imp

from django.conf import settings
from django.utils.importlib import import_module

from avocado.exceptions import RegisterError, AlreadyRegisteredError
from avocado.utils.camel import uncamel

class Library(object):
    superclass = None
    module_name = None
    suffix = ''
    default = None

    def __init__(self):
        self._cache = {}
        self._loaded = False
        self._discovery = False

    def _clean_name(self, name):
        if self.suffix and name.endswith(self.suffix):
            name = name[:-len(self.suffix)]
        return uncamel(name)

    def _get_class_name(self, klass):
        if hasattr(klass, 'name'):
            return klass.name
        return self._clean_name(klass.__name__)

    def add_object(self, class_name, obj, errmsg=''):
        store = self.get_store()
        # if already registered under the same name, test if the classes are
        # the same -- replace if true, throw error if not
        if store.has_key(class_name):
            robj = store.get(class_name)
            if obj.__class__ is not robj.__class__:
                raise AlreadyRegisteredError, errmsg
        store.update({class_name: obj})

    def remove_object(self, class_name):
        store = self.get_store()
        if store.has_key(class_name):
            store.remove(class_name)

    def get_store(self):
        if not self._cache and not self._loaded:
            self.autodiscover()
        return self._cache

    def register_object(self, class_name, obj):
        self.add_object(class_name, obj)

    def unregister_object(self, class_name):
        self.remove_object(class_name)

    def register(self, klass):
        if not issubclass(klass, self.superclass):
            raise RegisterError, '%s must be a subclass of %s' % (repr(klass),
                self.superclass.__name__)

        obj = klass()
        class_name = self._get_class_name(klass)

        self.register_object(class_name, obj)
        return klass

    def unregister(self, klass):
        class_name = self._get_class_name(klass)
        self.unregister_object(class_name)

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        store = self.get_store()
        choices = []
        for name in store.keys():
            choices.append((name, name))
        return choices

    def get(self, name):
        "Retrieve the cached instance given the name it is registered under."
        return self.get_store().get(name, self.default)

    def autodiscover(self):
        if self._discovery:
            return

        self._discovery = True

        for app in settings.INSTALLED_APPS:
            try:
                app_path = import_module(app).__path__
            except AttributeError:
                continue
            try:
                imp.find_module(self.module_name, app_path)
            except ImportError:
                continue

            import_module('%s.%s' % (app, self.module_name))

        self._discovery = False

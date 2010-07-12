from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary

class AbstractView(object):
    "The AbstractView implements a callable interface for a given view type."
    def __call__(self, *args, **kwargs):
        return self.respond(*args, **kwargs)
    
    def respond(self, *args, **kwargs):
        raise NotImplementedError


class GenericFormView(AbstractView):
    def respond(self, concept):
        return {'form': concept.form()}


class ViewLibrary(BaseLibrary):
    "The base class for defining the translator library."
    STORE_KEY = 'views'

    def _get_store(self, key=None):
        return self._cache

    def _fmt_name(self, name):
        return super(ViewLibrary, self)._fmt_name(name, 'View')

    def _register(self, klass_name, obj):
        self._add_item(None, klass_name, obj)

    def register(self, klass):
        return super(ViewLibrary, self).register(klass, AbstractView)

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache.keys()]

    def get_response(self, vtype, name, concept):
        view = self.get(vtype, name)
        return view(concept)


library = ViewLibrary()
library.register(GenericFormView)

# find all other views
library.autodiscover(avs.VIEW_MODULE_NAME)

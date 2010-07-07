from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary

class AbstractView(object):
    "The AbstractView implements a callable interface for a given view type."
    apply_to_all = False
    
    def __call__(self, vtype, concept):
        return getattr(self, vtype)(concept)


class ViewLibrary(BaseLibrary):
    """This library dynamically determines the available view types via a
    user-defined setting `VIEW_TYPES' part of the 'AVOCADO_SETTINGS'. This
    provides the available to define any number of view types without
    needing to subclass or override any part of the library. An example as
    follows:

        VIEW_TYPES = [{
            'form': {
                'name': 'Traditional',
            },
            'graphic' : {
                'name': 'Graphical',
            }
        }]

    Every view registered must be a sublcass of the AbstractView class. Each
    view can support any number of view types by simply defining a method of
    the same name, e.g:

        class MyView(AbstractView):
            def form(self, concept):
                form = concept.form()
                return {'form': form}

    The above view class defines the `form' method which returns a dictionary
    to be added to the Context of the response to the client.
    """
    
    # TODO add `attrs' parameter to VIEW_TYPES to restrict response object
    # and/or data types?
    STORE_KEY = 'views'
    VIEW_TYPES = avs.VIEW_TYPES

    def __init__(self, view_types=()):
        self._cache = {}
        
        for x in (view_types or self.VIEW_TYPES):
            self._cache.update(x)
        self.view_types = self._cache.keys()

        self._add_store()
    
    def _fmt_name(self, name):
        return super(ViewLibrary, self)._fmt_name(name, 'View')

    def _register(self, klass_name, obj):
        for vtype in self.view_types:
            if hasattr(obj, vtype) or obj.apply_to_all:
                self._add_item(vtype, klass_name, obj)

    def register(self, klass):
        return super(ViewLibrary, self).register(klass, AbstractView)

    def get_response(self, vtype, name, concept):
        view = self.get(vtype, name)
        return view(concept)


library = ViewLibrary()

# find all other views
library.autodiscover(avs.VIEW_MODULE_NAME)

from types import MethodType

from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary

class AbstractViewSet(object):
    "The AbstractViewSet class."
    order = ()
    
    def __call__(self, *args, **kwargs):
        return self._get_responses(*args, **kwargs)
    
    def _get_responses(self, *args, **kwargs):
        views = {}
        resps = []

        for name in dir(self):
            if name.startswith('_'):
                continue
            
            method = getattr(self, name)
            if type(method) is MethodType:
                resp = method(*args, **kwargs)
                if not resp.has_key('tabname'):
                    resp['tabname'] = name.replace('_', ' ').title()
                views[name] = resp

        if self.order:
            for x in self.order:
                resps.append(views.pop(x))
        resps.extend(views.values())

        return resps


class ViewSetLibrary(BaseLibrary):
    STORE_KEY = 'viewsets'

    def _get_store(self, key=None):
        return self._cache

    def _fmt_name(self, name):
        return super(ViewSetLibrary, self)._fmt_name(name, 'ViewSet')

    def _register(self, klass_name, obj):
        self._add_item(None, klass_name, obj)

    def register(self, klass):
        return super(ViewSetLibrary, self).register(klass, AbstractViewSet)

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache.keys()]

    def get(self, name, concept):
        viewset = super(ViewSetLibrary, self).get(None, name)
        return viewset(concept)


library = ViewSetLibrary()

# find all other views
library.autodiscover(avs.VIEW_MODULE_NAME)
import inspect

from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary

class AbstractViewSet(object):
    "The AbstractViewSet class."
    order = ()
    js = ''
    css = ''

    def __call__(self, concept, *args, **kwargs):
        fields = concept.fields.order_by('criterionfield__order')
        return self._get_responses(concept, fields, *args, **kwargs)

    def _get_responses(self, concept, fields, *args, **kwargs):
        views = []
        resps = {}

        for name in dir(self):
            if name.startswith('_'):
                continue

            method = getattr(self, name)
            if inspect.ismethod(method):
                resp = method(concept, fields, *args, **kwargs)
                if not resp.has_key('tabname'):
                    resp['tabname'] = name.replace('_', ' ').title()
                resps[name] = resp

        if self.order:
            for x in self.order:
                views.append(resps.pop(x))

        # add rest of un-ordered views
        views.extend(resps.values())

        # TODO add caching mechanism to try and fetch this before
        # rebuilding it
        resp = {
            'pk': concept.id,
            'name': concept.name,
            'js': self.js or None,
            'css': self.css or None,
            'views': views,
        }

        return resp


class ViewSetLibrary(BaseLibrary):
    STORE_KEY = 'viewsets'

    def _get_store(self, key=None):
        return self._cache

    def _format_name(self, name):
        return super(ViewSetLibrary, self)._format_name(name, 'ViewSet')

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

import inspect

from avocado.conf import settings
from avocado.concepts.library import Library

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

class ViewSetLibrary(Library):
    superclass = AbstractViewSet
    module_name = settings.VIEWSET_MODULE_NAME
    suffix = 'ViewSet'

    def get(self, name, concept):
        viewset = super(ViewSetLibrary, self).get(name)
        return viewset(concept)


library = ViewSetLibrary()
library.autodiscover()

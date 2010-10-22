import inspect

from avocado.conf import settings
from avocado.concepts.library import Library

class AbstractViewSet(object):
    "The AbstractViewSet class."
    order = ()
    js = ''
    css = ''

    def __call__(self, concept, *args, **kwargs):
        cfields = list(concept.conceptfields.order_by('order'))
        return self._get_responses(concept, cfields, *args, **kwargs)

    def _get_responses(self, concept, cfields, *args, **kwargs):
        views = []
        resps = {}

        for name in dir(self):
            if name.startswith('_'):
                continue

            method = getattr(self, name)
            if inspect.ismethod(method):
                resp = method(concept, cfields, *args, **kwargs)
                if not resp.has_key('tabname'):
                    resp['tabname'] = name.replace('_', ' ').title()
                resps[name] = resp

        if self.order:
            for x in self.order:
                views.append(resps.pop(x))

        # add rest of un-ordered views
        views.extend(resps.values())

        resp = {
            'id': concept.id,
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

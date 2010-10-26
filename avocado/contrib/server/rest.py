from django.http import HttpResponseNotAllowed
from django.core.urlresolvers import get_callable

HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'TRACE', 'OPTIONS', 'CONNECT')

def dispatcher(request, *args, **kwargs):
    """A simple dispatcher hook for url patterns.

    An example:

        urlpatterns = patterns('',
            url(r'^blog/$', dispatcher, {
                'methods': {
                    'GET': 'blog.read',
                    'PUT': 'blog.create',
                }
            }),

            url(r'^blog/(?P<id>\d+)/$', dispatcher, {
                'methods': {
                    'GET': 'blog.read_entry',
                    'POST': 'blog.update_entry',
                    'DELETE': 'blog.delete_entry',
                }
            })
        )
    """

    method = request.method
    allowed_methods = kwargs.pop('methods', {})

    if not allowed_methods or method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods.keys())

    view = get_callable(allowed_methods[method])
    return view(request, *args, **kwargs)

class HttpMethodDispatcher(object):
    "A class-based dispatcher which contains the views for each http method."

    allowed_methods = ('GET',)
    view_prefix = 'http_%s'

    def __call__(self, request, *args, **kwargs):
        method = request.method

        if method not in self.allowed_methods:
            raise HttpResponseNotAllowed(self.allowed_methods)

        view = self._get_view(method)

    def _get_view(self, method):
        return getattr(self, self.view_prefix % method.lower())

    def register(self, method, view):
        setattr(self, self.view_prefix % method.lower(), view)

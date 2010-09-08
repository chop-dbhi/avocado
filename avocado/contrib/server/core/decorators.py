from functools import wraps

from django.http import HttpResponseBadRequest

def ajax_only(view_or_methods):
    """Simple decorator to only accept ajax requests. Optionally takes a
    HTTP method.
    >>> from django.http import HttpRequest
    >>> request = HttpRequest()
    >>> request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
    >>> request.method = 'GET'

    >>> @ajax_only('get')
    ... def view(request, *args, **kwargs):
    ...    pass
    ...

    >>> @ajax_only('post')
    ... def view2(request, *args, **kwargs):
    ...   pass
    ...

    >>> @ajax_only
    ... def view3(request, *args, **kwargs):
    ...   pass
    ...

    >>> view(request)

    >>> request.method = 'POST'
    >>> isinstance(view(request), HttpResponseBadRequest)
    True
    >>> view2(request)
    >>> view3(request)

    >>> request.META['HTTP_X_REQUESTED_WITH'] = ''
    >>> isinstance(view(request), HttpResponseBadRequest)
    True

    >>> isinstance(view2(request), HttpResponseBadRequest)
    True

    >>> isinstance(view3(request), HttpResponseBadRequest)
    True
    """
    view = None
    methods = []

    if callable(view_or_methods):
        view = view_or_methods
    else:
        if isinstance(view_or_methods, basestring):
            methods = [view_or_methods]
        methods = map(lambda x: x.lower(), methods)

    def decorator(view_func):
        def _view_func(request, *args, **kwargs):
            if not request.is_ajax():
                return HttpResponseBadRequest()
            if methods:
                if request.method.lower() not in methods:
                    return HttpResponseBadRequest()
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(_view_func)

    if view:
        return decorator(view)
    return decorator

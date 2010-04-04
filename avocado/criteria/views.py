"""
The `CriterionConceptViewLibrary' provides a very basic interface to store
and get registered views that handle the logic for a `CriterionConcept' object.

The implementation of the views and urls are left up the project implementer.
"""

import imp
from functools import wraps
from django.conf import settings
from django.utils.importlib import import_module

LOADING = False

def autodiscover():
    global LOADING

    if LOADING:
        return
    LOADING = True

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('formatters', app_path)
        except ImportError:
            continue

        import_module('%s.views' % app)

    LOADING = False


class CriterionConceptViewLibrary(object):
    """A simple datastructure that acts as a library for registering and
    managing formatters.
    """
    def __init__(self):
        self._views = {}

    def register(self, view_name=None):
        "Registers a views with an optional name."
        def decorator(view):
            if view_name and callable(view_name):
                _name = view_name.__name__
            else:
                _name = view_name

            self._views[view.__name__] = (_name, view)

            def _view(*args, **kwargs):
                return view(*args, **kwargs)
            return wraps(view)(_view)

        if view_name and callable(view_name):
            return decorator(view_name)
        return decorator

    def choices(self):
        "Returns a tuple of pairs that can be used as choices in a form."
        return tuple([(x, y[0]) for x, y in self._views.items()])
    
    def get(self, view_name):
        name, view = self._views.get(view_name, (None, None))
        return view

library = CriterionConceptViewLibrary()

autodiscover()
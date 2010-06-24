import imp
from copy import deepcopy

from django.utils.importlib import import_module

from avocado.settings import settings
from avocado.utils.camel import camelcaser
from avocado.exceptions import AlreadyRegisteredError, RegisterError

class AbstractView(object):
    "The AbstractView implements a callable interface for a given view type."
    def __call__(self, vtype, concept):
        return getattr(self, vtype)(concept)


class ViewLibrary(object):
    """This library dynamically determines the available view types via a
    user-defined setting `VIEW_TYPES' part of the 'AVOCADO_SETTINGS'. This
    provides the available to define any number of view types without
    needing to subclass or override any part of the library. An example as
    follows:

        VIEW_TYPES = {
            'form': {
                'name': 'Traditional',
            },
            'graphic' : {
                'name': 'Graphical',
            }
        }

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

    VIEW_TYPES = settings.VIEW_TYPES

    def __init__(self, view_types={}):
        self._cache = deepcopy(view_types or self.VIEW_TYPES)
        for key in self._cache:
            self._cache[key]['views'] = {}
        self._vtypes = self._cache.keys()

    def _parse_name(self, name):
        if name.endswith('View'):
            name = name[:-4]
        toks = [name[0]]
        for x in name[1:]:
            if x.isupper():
                toks.append(' ')
            toks.append(x)
        return ''.join(toks)

    def _add_view(self, vtype, klass_name, obj):
        if self._cache[vtype]['views'].has_key(klass_name):
            raise AlreadyRegisteredError, 'A view with the ' \
                'name "%s" is already registered for the %s ' \
                'view type' % (klass_name, vtype)
        self._cache[vtype]['views'][klass_name] = obj

    def register(self, klass):
        "Registers a AbstractView subclass. The class name must be unique."
        if not issubclass(klass, AbstractView):
            raise RegisterError, '%s must be a subclass of AbstractView' % repr(klass)

        obj = klass()

        if hasattr(klass, 'name'):
            klass_name = klass.name
        else:
            klass_name = self._parse_name(klass.__name__)

        for vtype in self._vtypes:
            if hasattr(obj, vtype):
                self._add_view(vtype, klass_name, obj)
        return klass

    def choices(self, vtype):
        "Returns a list of tuples that can be used as choices in a form."
        choices = []
        for name, obj in self._cache[vtype]['views'].items():
            if obj.is_choice:
                choices.append((name, name))
        return choices
    
    def get(self, vtype, name):
        return self._cache[vtype]['views'].get(name)
    
    def get_response(self, vtype, name, concept):
        view = self.get(vtype, name)
        return camelcaser.camel_keys(view(concept))


library = ViewLibrary()

LOADING = False

def autodiscover():
    global LOADING

    if LOADING:
        return
    LOADING = True

    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('views', app_path)
        except ImportError:
            continue

        import_module('%s.views' % app)

    LOADING = False

autodiscover()

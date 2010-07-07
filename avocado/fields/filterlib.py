from django.db.models import Q

from avocado.settings import settings as avs
from avocado.concepts.library import BaseLibrary

class AbstractFilter(object):
    """Provides the logic necessary to return a Q object for altering a
    QuerySet object.

    There are 3 components necessary for specifying conditions:
        - the ModelTree object
        - CriterionConcept fields
        - the logic tree
    """
    def __call__(self, *args, **kwargs):
        return self.filter(*args, **kwargs)

    def _clean(self, field, value, *args, **kwargs):
        "Cleans `value' according to `field'."
        is_valid, cleaned_value, errors = field.clean_value(value, *args, **kwargs)
        return cleaned_value

    def _rel_path(self, modeltree, field, operator):
        nodes = modeltree.path_to(field.model)
        return modeltree.query_string(nodes, field.field_name, operator)

    def filter(self, modeltree, field, operator, value):
        raise NotImplementedError


class SimpleFilter(AbstractFilter):
    def filter(self, modeltree, field, operator, value):
        key = self._rel_path(modeltree, field, operator)
        cleaned_value = self._clean(field, value)
        return Q(**{key: cleaned_value})


class FilterLibrary(BaseLibrary):
    "The base class for defining a filter library."
    STORE_KEY = 'filters'
    
    def _get_store(self, key=None):
        return self._cache

    def _fmt_name(self, name):
        return super(FilterLibrary, self)._fmt_name(name, 'Filter')
    
    def _register(self, klass_name, obj):
        self._add_item(None, klass_name, obj)

    def register(self, klass):
        return super(FilterLibrary, self).register(klass, AbstractFilter)

    def choices(self):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache.keys()]


library = FilterLibrary()
library.register(SimpleFilter)

# find all other filters
library.autodiscover(avs.FILTER_MODULE_NAME)
"Caching utilities for the `fields' package."
from django.core.cache import cache

from avocado.fields.models import FieldConcept

FIELD_CACHE_KEY = 'avocado:fieldconcept:%s'

def get_concept(concept_id, queryset=None, ret_val=None):
    """Simple interface for getting (and setting) a concept from global cache.

    If provided, the optional `queryset' is used to fetch the concept from.
    This is useful primarily for restricting access to certain concepts.
    """
    key = FIELD_CACHE_KEY % concept_id

    concept = cache.get(key, None)
    if concept is None:
        try:
            if queryset is not None:
                concept = queryset.get(id=concept_id)
            else:
                concept = FieldConcept.objects.get(id=concept_id)
        except FieldConcept.DoesNotExist:
            return ret_val
        cache.set(key, concept)
    return concept

def get_concepts(concept_ids, queryset=None):
    "Returns a generator of concept objects."
    for id_ in concept_ids:
        yield get_concept(id_, queryset=queryset)

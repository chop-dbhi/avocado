"Caching utilities for the `columns' package."
from django.core.cache import cache

from avocado.columns.models import ColumnConcept

COLUMN_CACHE_KEY = 'avocado:columnconcept:%s'
COLUMN_FIELD_CACHE_KEY = 'avocado:columnconcept:fields:%s'

def get_concept(concept_id, queryset=None, ret_val=None):
    """Simple interface for getting (and setting) a concept from global cache.
    
    If provided, the optional `queryset' is used to fetch the concept from.
    This is useful primarily for restricting access to certain concepts.
    """
    key = COLUMN_CACHE_KEY % concept_id

    concept = cache.get(key, None)
    if concept is None:
        try:
            if queryset is not None:
                concept = queryset.get(id=concept_id)
            else:
                concept = ColumnConcept.objects.get(id=concept_id)
        except ColumnConcept.DoesNotExist:
            return ret_val
        cache.set(key, concept)
    return concept

def get_concept_fields(concept, queryset=None, ret_val=None):
    """Simple interface for getting (and setting) a concept's fields
    from global cache. `concept' can be an object or a integer.
    
    The optional `queryset' parameter simply passes it to `get_concept'
    if called.
    """
    if isinstance(concept, ColumnConcept):
        inst = True
        key = COLUMN_FIELD_CACHE_KEY % concept.id
    else:
        inst = False
        key = COLUMN_FIELD_CACHE_KEY % concept

    fields = cache.get(key, None)
    if fields is None:
        if not inst:
            concept = get_concept(concept, queryset)
            if concept is None:
                return ret_val
        fields = list(concept.fields.order_by('columnconceptfield__order'))
        cache.set(key, fields)
    return fields

def get_concepts(concept_ids, queryset=None):
    "Returns a generator of concept objects."
    for id_ in concept_ids:
        yield get_concept(id_, queryset=queryset)

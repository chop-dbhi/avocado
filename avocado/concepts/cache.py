from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

class ConceptCache(object):
    CACHE_KEY = 'avocado:%s:%s'
    FIELD_CACHE_KEY = 'avocado:%s:fields:%s'
    
    def get(self, concept_id, queryset, ret_val=None):
        "Simple interface for getting (and setting) a concept from global cache."
        key = self.CACHE_KEY % (queryset.model.__name__.lower(), concept_id)

        concept = cache.get(key, None)
        if concept is None:
            try:
                concept = queryset.get(id=concept_id)
            except ObjectDoesNotExist:
                return ret_val
            cache.set(key, concept)
        return concept

    def get_many(self, concept_ids, queryset=None):
        "Returns a generator of concept objects."
        for cid in concept_ids:
            yield self.get(cid, queryset=queryset)


    def get_fields(self, concept_id, queryset, ret_val=None):
        """Simple interface for getting (and setting) a concept's fields
        from global cache. `concept' can be an object or a integer.
    
        The optional `queryset' parameter simply passes it to `self.get'
        if called.
        """
        key = self.FIELD_CACHE_KEY % (queryset.model.__name__.lower(), concept_id)

        fields = cache.get(key, None)
        if fields is None:
            concept = self.get(concept_id, queryset)
            if concept is None:
                return ret_val
            fields = list(concept.fields.order_by('criterionconceptfield__order'))
            cache.set(key, fields)
        return fields
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

class ConceptCache(object):
    def __init__(self, model_name):
        self.id_key = ':'.join(['avocado', model_name, '%s'])
        self.field_id_key = ':'.join(['avocado', model_name, '%s', 'fields'])

    def get(self, concept_id, queryset=None, ret_val=None):
        "Simple interface for getting (and setting) a concept from global cache."
        key = self.id_key % concept_id

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
        concepts = []
        for cid in concept_ids:
            concepts.append(self.get(cid, queryset=queryset))
        return concepts


    def get_fields(self, concept_id, queryset, ret_val=None):
        """Simple interface for getting (and setting) a concept's fields
        from global cache. `concept' can be an object or a integer.

        The optional `queryset' parameter simply passes it to `self.get'
        if called.
        """
        key = self.field_id_key % concept_id

        fields = cache.get(key, None)
        if fields is None:
            concept = self.get(concept_id, queryset, ret_val)
            if concept == ret_val:
                return ret_val
            fields = list(concept.fields.order_by('conceptfield__order'))
            cache.set(key, fields)
        return fields

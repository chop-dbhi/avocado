from avocado.concepts.cache import ConceptCache
from avocado.fields.models import FieldConcept

class FieldConceptCache(ConceptCache):
    def get(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = FieldConcept.objects.all()
        return super(FieldConceptCache, self).get(concept_id, queryset, ret_val)
    
    def get_fields(self, concept_ids, queryset=None, ret_val=None):
        raise NotImplementedError


cache = FieldConceptCache()
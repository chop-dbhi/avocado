from avocado.concepts.cache import ConceptCache
from avocado.criteria.models import CriterionConcept

class CriterionConceptCache(ConceptCache):
    def get(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = CriterionConcept.objects.all()
        return super(CriterionConceptCache, self).get(concept_id, queryset, ret_val)
    
    def get_fields(self, concept_ids, queryset=None, ret_val=None):
        if queryset is None:
            queryset = CriterionConcept.objects.all()
        return super(CriterionConceptCache, self).get_fields(concept_ids, queryset, ret_val)


cache = CriterionConceptCache()
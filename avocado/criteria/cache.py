from avocado.concepts.cache import ConceptCache
from avocado.criteria.models import Criterion

class CriterionCache(ConceptCache):
    def get(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = Criterion.objects.all()
        return super(CriterionCache, self).get(concept_id=concept_id,
            queryset=queryset, ret_val=ret_val)
    
    def get_fields(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = Criterion.objects.all()
        return super(CriterionCache, self).get_fields(concept_id=concept_id,
            queryset=queryset, ret_val=ret_val)


cache = CriterionCache(Criterion.__name__.lower())
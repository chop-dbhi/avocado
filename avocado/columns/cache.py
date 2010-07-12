from avocado.concepts.cache import ConceptCache
from avocado.columns.models import ColumnConcept

class ColumnConceptCache(ConceptCache):
    def get(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = ColumnConcept.objects.all()
        return super(ColumnConceptCache, self).get(concept_id, queryset, ret_val)
    
    def get_fields(self, concept_ids, queryset=None, ret_val=None):
        if queryset is None:
            queryset = ColumnConcept.objects.all()
        return super(ColumnConceptCache, self).get_fields(concept_ids, queryset, ret_val)


cache = ColumnConceptCache()
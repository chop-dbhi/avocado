from avocado.concepts.cache import ConceptCache
from avocado.columns.models import Column

class ColumnCache(ConceptCache):
    def get(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = Column.objects.all()
        return super(ColumnCache, self).get(concept_id=concept_id,
            queryset=queryset, ret_val=ret_val)

    def get_fields(self, concept_id, queryset=None, ret_val=None):
        if queryset is None:
            queryset = Column.objects.all()
        return super(ColumnCache, self).get_fields(concept_id=concept_id,
            queryset=queryset, ret_val=ret_val)


cache = ColumnCache(Column.__name__.lower())

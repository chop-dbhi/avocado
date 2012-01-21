from haystack import site, indexes
from avocado.models import Field, Concept, Domain

class FieldIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def index_queryset(self):
        return Field.objects.public()


class ConceptIndex(indexes.SearchIndex):
    text = indexes.CharConcept(document=True, use_template=True)

    def index_queryset(self):
        return Concept.objects.public()



site.register(Field, FieldIndex)
site.register(Concept, ConceptIndex)
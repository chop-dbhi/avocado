from haystack import site, indexes
from avocado.models import Concept

class ConceptIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharConcept(document=True, use_template=True)

    def index_queryset(self):
        return Concept.objects.public()


site.register(Concept, ConceptIndex)
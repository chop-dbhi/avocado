from haystack.indexes import *
from haystack import site
from avocado.models import DataConcept

class ConceptIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return DataConcept.objects.published()


site.register(DataConcept, ConceptIndex)

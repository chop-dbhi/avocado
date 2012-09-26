from haystack import site, indexes
from avocado.models import DataConcept, DataField


class DataConceptIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return DataConcept


class DataFieldIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return DataField


site.register(DataField, DataFieldIndex)
site.register(DataConcept, DataConceptIndex)

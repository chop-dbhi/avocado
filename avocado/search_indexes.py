from haystack import site
from haystack.indexes import *
from avocado.models import DataConcept, DataField


class DataConceptIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def get_model(self):
        return DataConcept


class DataFieldIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def get_model(self):
        return DataField


site.register(DataField, DataFieldIndex)
site.register(DataConcept, DataConceptIndex)

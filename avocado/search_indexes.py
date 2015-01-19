from haystack import indexes
from avocado.models import DataConcept, DataField


class DataIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    text_auto = indexes.EdgeNgramField(use_template=True)

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(published=True, archived=False)

    def read_queryset(self, using=None):
        return self.index_queryset()

    def load_all_queryset(self):
        return self.index_queryset()


class DataConceptIndex(DataIndex, indexes.Indexable):
    def get_model(self):
        return DataConcept


class DataFieldIndex(DataIndex, indexes.Indexable):
    def get_model(self):
        return DataField

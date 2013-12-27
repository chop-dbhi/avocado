import warnings
from haystack import indexes
from avocado.conf import settings
from avocado.models import DataConcept, DataField

# Warn if either of the settings are set to false
if not getattr(settings, 'CONCEPT_SEARCH_ENABLED', True) or \
        not getattr(settings, 'FIELD_SEARCH_ENABLED', True):
    warnings.warn('CONCEPT_SEARCH_ENABLED and FIELD_SEARCH_ENABLED have been '
                  'deprecated due to changes in Haystack 2.x API. To exclude '
                  'an index from being discovered, add the path to the class '
                  'to EXCLUDED_INDEXES in the appropriate '
                  'HAYSTACK_CONNECTIONS entry in settings.')


class DataIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    text_auto = indexes.EdgeNgramField(use_template=True)

    def index_queryset(self, using=None):
        return self.get_model().objects.published()

    def load_all_queryset(self):
        return self.index_queryset()


class DataConceptIndex(DataIndex, indexes.Indexable):
    def get_model(self):
        return DataConcept


class DataFieldIndex(DataIndex, indexes.Indexable):
    def get_model(self):
        return DataField

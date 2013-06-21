from haystack import site
from haystack.indexes import *
from avocado.conf import settings
from avocado.models import DataConcept, DataField


class DataConceptIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    text_auto = EdgeNgramField(use_template=True)

    def index_queryset(self):
        return DataConcept.objects.published()


class DataFieldIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    text_auto = EdgeNgramField(use_template=True)

    def index_queryset(self):
        return DataField.objects.published()


if settings.CONCEPT_SEARCH_ENABLED:
    site.register(DataConcept, DataConceptIndex)

if settings.FIELD_SEARCH_ENABLED:
    site.register(DataField, DataFieldIndex)

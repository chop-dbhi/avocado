"""
The Column class takes an optional setting, 'COLUMN_CONCEPT_MIXIN' which
defines an abstract Model class that can provide references to additional
fields.

The most typical scenario for using this setting is to specify 'formatter'
fields for the Column class to use.
"""

from django.db import models

from avocado.concepts.models import Concept, ConceptField
from avocado.fields.models import ModelField
from avocado.columns.mixins import ColumnMixin

__all__ = ('Column', 'ColumnField')

class Column(Concept, ColumnMixin):
    "An interface to specify the necessary fields for a column."
    fields = models.ManyToManyField(ModelField, through='ColumnField')

    class Meta(Concept.Meta):
        pass


class ColumnField(ConceptField):
    concept = models.ForeignKey(Column)
    field = models.ForeignKey(ModelField)

    class Meta(ConceptField.Meta):
        pass

"""
The ColumnConcept class takes an optional setting, 'COLUMN_CONCEPT_MIXIN' which
defines an abstract Model class that can provide references to additional
fields.

The most typical scenario for using this setting is to specify 'formatter'
fields for the ColumnConcept class to use.
"""

from django.db import models

from avocado.concepts.models import Concept, ConceptField
from avocado.fields.models import FieldConcept
from avocado.columns.mixins import ColumnConceptMixin

__all__ = ('ColumnConcept', 'ColumnConceptField')

class ColumnConcept(Concept, ColumnConceptMixin):
    "An interface to specify the necessary fields for a column."
    fields = models.ManyToManyField(FieldConcept, through='ColumnConceptField')

    class Meta(Concept.Meta):
        verbose_name = 'column concept'
        verbose_name_plural = 'column concepts'


class ColumnConceptField(ConceptField):
    concept = models.ForeignKey(ColumnConcept)

    class Meta(ConceptField.Meta):
        verbose_name = 'column concept field'
        verbose_name_plural = 'column concept fields'

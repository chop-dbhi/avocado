"""
The ColumnConcept class takes an optional setting, 'COLUMN_CONCEPT_MIXIN' which
defines an abstract Model class that can provide references to additional
fields.

The most typical scenario for using this setting is to specify 'formatter'
fields for the ColumnConcept class to use.
"""

from django.db import models

from avocado.settings import settings
from avocado.concepts.models import ConceptAbstract, ConceptFieldAbstract
from avocado.fields.models import FieldConcept

__all__ = ('ColumnConcept', 'ColumnConceptField')

ColumnConceptMixin = settings.COLUMN_CONCEPT_MIXIN

class ColumnConcept(ConceptAbstract, ColumnConceptMixin):
    "An interface to specify the necessary fields for a column."
    fields = models.ManyToManyField(FieldConcept, through='ColumnConceptField')

    class Meta(ConceptAbstract.Meta):
        verbose_name = 'column concept'
        verbose_name_plural = 'column concepts'


class ColumnConceptField(ConceptFieldAbstract):
    concept = models.ForeignKey(ColumnConcept)

    class Meta(ConceptFieldAbstract.Meta):
        verbose_name = 'column concept field'
        verbose_name_plural = 'column concept fields'

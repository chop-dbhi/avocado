"""
The ColumnConcept class takes an optional setting, 'COLUMN_CONCEPT_MIXIN' which
defines an abstract Model class that can provide references to additional
fields.

The most typical scenario for using this setting is to specify 'formatter'
fields for the ColumnConcept class to use.
"""

from django.db import models
from django.conf import settings

from avocado.concepts.models import ConceptAbstract, ConceptFieldAbstract
from avocado.concepts.managers import ConceptManager
from avocado.fields.models import FieldConcept

__all__ = ('ColumnConcept', 'ColumnConceptField')

ColumnConceptMixin = getattr(settings, 'COLUMN_CONCEPT_MIXIN', models.Model)

class ColumnConcept(ConceptAbstract, ColumnConceptMixin):
    "An interface to specify the necessary fields for a column."
    fields = models.ManyToManyField(FieldConcept, through='ColumnConceptField')

    objects = ConceptManager()

    class Meta(ConceptAbstract.Meta):
        verbose_name = 'column concept'
        verbose_name_plural = 'column concepts'


class ColumnConceptField(ConceptFieldAbstract):
    concept = models.ForeignKey(ColumnConcept)

    class Meta(ConceptFieldAbstract.Meta):
        verbose_name = 'column concept field'
        verbose_name_plural = 'column concept fields'

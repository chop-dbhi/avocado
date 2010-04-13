from django.db import models

from avocado.concepts.models import ConceptAbstract, ConceptFieldAbstract
from avocado.concepts.managers import ConceptManager
from avocado.fields.models import FieldConcept
from avocado.columns.formatters import library

__all__ = ('ColumnConcept', 'ColumnConceptField')

class ColumnConcept(ConceptAbstract):
    "An interface to specify the necessary fields for a column."
    raw_formatter = models.CharField(max_length=100, blank=True,
        choices=library.choices('raw'))
    pretty_formatter = models.CharField(max_length=100, blank=True,
        choices=library.choices('pretty'))
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

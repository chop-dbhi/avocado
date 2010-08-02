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
    
    def add_fields_to_queryset(self, queryset, modeltree):
        fields = self.fields.all()
        aliases = []
        for f in fields:
            queryset = modeltree.add_joins(f.model, queryset)
            aliases.append((f.model._meta.db_table, f.field_name))
        return (queryset, aliases)
    
    def get_ordering_for_queryset(self, modeltree, direction='asc'):
        fields = self.fields.all()
        orders = []
        for f in fields:
            orders.append(f.order_string(modeltree, direction))
        return orders

class ColumnField(ConceptField):
    concept = models.ForeignKey(Column)
    field = models.ForeignKey(ModelField)

    class Meta(ConceptField.Meta):
        pass

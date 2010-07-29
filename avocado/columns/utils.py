from django.utils.datastructures import SortedDict

from avocado.concepts.utils import ConceptSet
from avocado.columns.models import Column
from avocado.columns.cache import cache

def get_columns(concept_ids, queryset=None):
    """Simple helper to retrieve an ordered list of columns. Columns that are
    not found are simply ignored.
    """
    concepts = []
    for concept in cache.get_many(concept_ids, queryset):
        if concept is not None:
            concepts.append(concept)
    return concepts

def get_column_orders(column_orders, queryset=None):
    columns = SortedDict({})
    for order, (pk, direction) in enumerate(column_orders):
        column = cache.get(pk, queryset)
        if column is None:
            continue
        kwarg = {column: {'direction': direction, 'order': order}}
        columns.update(kwarg)
    return columns

class ColumnSet(ConceptSet):
    """A ColumnSet provides a simple interface to alter querysets in terms
    of adding additional columns and adding column ordering.
    """
    def __setstate__(self, state):
        queryset = Column.objects.all()
        super(ColumnSet, self).__setstate__(state, queryset)

    def add_columns(self, queryset, columns):
        """Takes a `queryset' and ensures the proper table join have been
        setup to display the table columns.
        """
        # TODO determine if the aliases can contain more than one reference
        # to a table
        
        # add queryset model's pk field
        aliases = [(queryset.model._meta.db_table,
            queryset.model._meta.pk.column)]

        for column in columns:
            fields = cache.get_fields(column, self.queryset)

            for field in fields:
                model = field.model
                aliases.append((model._meta.db_table, field.field_name))
                queryset = self.modeltree.add_joins(model, queryset)

        queryset.query.select = aliases

        return queryset

    def add_ordering(self, queryset, column_orders):
        """Applies column ordering to a queryset. Resolves a Column's
        fields and generates the `order_by' paths.
        """
        queryset.query.clear_ordering()
        orders = []

        for column, direction in column_orders:
            fields = cache.get_fields(column, self.queryset)

            for field in fields:
                order = field.query_string(modeltree=self.modeltree)

                if direction.lower() == 'desc':
                    order = '-' + order
                orders.append(order)

        return queryset.order_by(*orders)

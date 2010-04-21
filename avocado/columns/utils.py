from django.utils.datastructures import SortedDict

from avocado.concepts.utils import ConceptSet
from avocado.columns.models import ColumnConcept
from avocado.columns.cache import get_concept, get_concepts, get_concept_fields

def get_columns(concept_ids, queryset=None):
    """Simple helper to retrieve an ordered list of columns. Columns that are
    not found are simply ignored.
    """
    concepts = []
    for concept in get_concepts(concept_ids, queryset):
        if concept is not None:
            concepts.append(concept)
    return concepts

def get_column_orders(column_orders, queryset=None):
    columns = SortedDict({})
    for i, (id_, direction) in enumerate(column_orders):
        column = get_concept(id_, queryset)
        if column is None:
            continue
        dict_ = {column: {'direction': direction, 'order': i}}
        columns.update(dict_)
    return columns

class ColumnSet(ConceptSet):
    """A ColumnSet provides a simple interface to alter querysets in terms
    of adding additional columns and adding column ordering.
    """
    def __setstate__(self, dict_):
        queryset = ColumnConcept.objects.all()
        super(ColumnConcept, self).__setstate__(dict_, queryset)

    def add_columns(self, queryset, concepts):
        """Takes a `queryset' and ensures the proper table join have been
        setup to display the table columns.        
        """
        aliases = [(queryset.model._meta.db_table,
            queryset.model._meta.pk.column)]

        for concept in concepts:
            fields = get_concept_fields(concept, self.queryset)

            for field in fields:
                model = field.model_cls
                aliases.append((model._meta.db_table, field.field_name))

                # only apply join if the table does not already exist in the query
                if model._meta.db_table not in queryset.query.tables:
                    nodes = self.model_tree.path_to(model)
                    conns = self.model_tree.get_all_join_connections(nodes)
                    for c in conns:
                        queryset.query.join(c, promote=True)

        queryset.query.select = aliases

        return queryset

    def add_ordering(self, queryset, concept_orders):
        """Applies column ordering to a queryset. Resolves a ColumnConcept's
        fields and generates the `order_by' paths.
        """
        queryset.query.clear_ordering()
        orders = []

        for concept, meta in concept_orders.items():
            fields = get_concept_fields(concept, self.queryset)

            for field in fields:
                path = []
                model = field.model_cls

                if self.model_tree.root_model != model:
                    nodes = self.model_tree.path_to(model)
                    path = self.model_tree.related_name_path(nodes)

                order = '__'.join(path + [field.field_name])

                if meta['direction'].lower() == 'desc':
                    order = '-' + order
                orders.append(order)

        return queryset.order_by(*orders)
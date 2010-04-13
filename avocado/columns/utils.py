from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import SortedDict

from avocado.columns.cache import get_column_fields

def get_columns(queryset, concept_ids):
    """Simple helper to retrieve an ordered list of columns. Columns that are
    not found are simply ignored.
    """
    concepts = []
    ignored = 0
    for id_ in concept_ids:
        try:
            concept = queryset.get(id=id_)
        except ObjectDoesNotExist:
            ignored += 1
            continue
        concepts.append(concept)
    return concepts, ignored

def get_column_orders(queryset, column_orders):
    columns = SortedDict({})
    ignored = 0
    for i, (id_, direction) in enumerate(column_orders):
        try:
            column = queryset.get(id=id_)
        except ObjectDoesNotExist:
            ignored += 1
            continue
        dict_ = {column: {'direction': direction, 'order': i}}
        columns.update(dict_)
    return columns, ignored

class ColumnSet(object):
    """A ColumnSet provides a simple interface to alter querysets in terms
    of adding additional columns and adding column ordering.

        `queryset' - a ColumnConcept queryset that acts as a starting point
        for retrieving objects from
        
        `modeltree' - a ModelTree instance that should have a root model that
        is the same as the queryset(s) being processed via the public methods
    """
    def __init__(self, queryset, model_tree):
        self.queryset = queryset
        self.model_tree = model_tree

    def add_columns(self, queryset, concepts):
        """Takes a `queryset' and ensures the proper table join have been
        setup to display the table columns.        
        """
        aliases = [(queryset.model._meta.db_table,
            queryset.model._meta.pk.column)]

        for concept in concepts:
            fields = get_column_fields(concept)

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
            fields = get_column_fields(concept)

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
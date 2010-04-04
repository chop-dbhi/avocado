from .models import ColumnConcept


class ColumnSetError(Exception):
    pass


class ColumnSet(object):
    """A ColumnSet provides a simple interface to alter querysets in terms
    of adding additional columns and adding column ordering.

    Fetching of particular ColumnConcepts must fail gracefully since the
    incoming `column_concepts' queryset may be filtered.
    """
    def __init__(self, column_concepts, model_tree):
        self.column_concepts = column_concepts
        self.model_tree = model_tree
        self._field_cache = {}

    def _get_fields(self, concept):
        """Helper method to retrieve-and-cache all fields assocated with a
        concept from local cache.
        """
        fields = self._field_cache.get(concept.id, None)
        if fields is None:
            fields = concept.fields.order_by('columnconceptfield__order')
            self._field_cache[concept.id] = fields
        return fields

    def _get_column_ordering(self, concept_orders):
        "Resolves a ColumnConcept's fields and generates the order by paths."
        column_orders = []

        for concept_id, direction in concept_orders:
            try:
                concept = self.column_concepts.get(id=concept_id)
            except ColumnConcept.DoesNotExist:
                continue

            fields = self._get_fields(concept)

            for field in fields:
                model = field.model_cls

                if self.model_tree.root_model != model:
                    nodes = self.model_tree.path_to(model)
                    # get the path as a string to setup joins
                    path = self.model_tree.related_name_path(nodes)

                order = '__'.join(path + [field.field_name])

                if direction.lower() == 'desc':
                    order = '-' + order
                column_orders.append(order)

        return column_orders

    def _get_column_aliases(self, queryset, concept_ids):
        """Fetches all fields associated with a set of ColumnConcepts and returns
        a sequence of tuples containing the database table name and the field
        name. This can be directly used with the BaseQuery.select attribute.

        TODO clean up how the `raw' and `pretty' attributes get set.
        """
        self.pretty = {'formatters': [], 'names': []}
        self.raw = {'formatters': [], 'names': []}

        column_aliases = []

        # add pk field of root model
        column_aliases.append((self.model_tree.root_model._meta.db_table,
            self.model_tree.root_model._meta.pk.column))

        for concept_id in concept_ids:
            try:
                concept = self.column_concepts.get(id=concept_id)
            except ColumnConcept.DoesNotExist:
                continue

            fields = self._get_fields(concept)

            for field in fields:
                column_aliases.append((field.model_cls._meta.db_table,
                        field.field_name))
                self.raw['names'].append(field.display_name)

            if len(fields) == 1:
                self.raw['names'] = [concept.name]

            self.pretty['names'].append(concept.name)

            self.pretty['formatters'].append((len(fields), concept.pretty_formatter))
            self.raw['formatters'].append((len(fields), concept.raw_formatter))

        return column_aliases

    def add_column_ordering(self, queryset, concept_orders):
        "Applies column ordering to a queryset."
        column_orders = self._get_column_ordering(concept_orders)
        return queryset.order_by(*column_orders)

    def add_columns(self, queryset, concept_ids):
        "Explicity sets the columns of a queryset."
        column_aliases = self._get_column_aliases(concept_ids)
        queryset.query.select = column_aliases
        return queryset

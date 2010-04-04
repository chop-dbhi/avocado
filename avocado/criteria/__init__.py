import time

#from avocado.fields.models import Field # TODO update this after refactor
from avocado.exceptions import PermissionDenied
from avocado.modeltree import ModelTree

class CriterionSet(object):
    """Provides the mechanism to validate and normalize user-defined criteria.
    This interface provides the mechanisms to filter down a queryset.

    `parsed_data' must be in the format:
        {<field_id>: {'op': u'foo', 'val': [u'11', u'39']}, ...}

    a dict with keys being the primary key of `Field' objects and the value
    being the choosen condition and params.

    The `queryset' must be provided as a starting point when fetching data
    about each criterion.
    """

    def __init__(self, queryset, parsed_data, model_tree):
        self.queryset = queryset
        self.parsed_data = parsed_data
        self.model_tree = model_tree

    def _get_criteria(self):
        """Iterates over the `parsed_data' and fetches the criterion objects
        from the database.
        """
        if not hasattr(self, '_criteria'):
            self._criteria = []

            for pk, dct in self.parsed_data.items():
                try:
                    c = self.queryset.get(id=pk)
                except self.queryset.model.DoesNotExist:
                    # block further processing, since this could be a breach
                    raise PermissionDenied

                # TODO add error catching..
                c.validate(dct['op'], dct['val'])

                self._criteria.append(c)

        return self._criteria
    criteria = property(_get_criteria)

    def _get_filters(self):
        if not hasattr(self, '_filters'):
            self._filters = []
            for c in self.criteria:
                model = c.model_cls
                field_name = c.field_name
                operator = c.op_obj.op
                value = c.val_obj
                is_negated = c.op_obj.is_negated
                path = []

                # initially test to see if the `model' is the same as
                # `model_tree.model'. no traversal is needed if they are the same
                if self.model_tree.root_model != model:
                    # get an ordered sequence of tree nodes that represents the shortest
                    # path to the give `model_class'
                    nodes = self.model_tree.path_to(model)
                    # get the path as a string to setup joins
                    path = self.model_tree.related_name_path(nodes)

                path.extend([field_name, operator])
                self._filters.append((is_negated, {str('__'.join(path)): value}))

        return self._filters
    filters = property(_get_filters)

    def add_filter(self, queryset):
        """Takes in a queryset and applies filters to it.
        TODO update to support OR's
        """
        for f in self.filters:
            queryset = queryset._filter_or_exclude(f[0], **f[1])
        return queryset

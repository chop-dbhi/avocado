from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def get_criteria(queryset, concept_ids):
    """Simple helper to retrieve an ordered list of criteria. Criteria that are
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

class CriterionSet(object):
    """Provides the mechanism to validate and normalize user-defined criteria.
    This interface provides the mechanisms to filter down a queryset.

    `pre_criteria' must be in the format:
        {<field_id>: {'op': u'foo', 'val': [u'11', u'39']}, ...}

    a dict with keys being the primary key of `Field' objects and the value
    being the choosen condition and params.

    The `queryset' must be provided as a starting point when fetching data
    about each criterion.
    """

    def __init__(self, queryset, model_tree):
        self.queryset = queryset
        self.model_tree = model_tree

    def _get_criteria(self, pre_criteria):
        """Iterates over the `pre_criteria' and fetches the criterion objects
        from the database.
        """
        criteria = []
        for pk, dct in pre_criteria.items():
            try:
                c = self.queryset.get(id=pk)
            except self.queryset.model.DoesNotExist:
                # block further processing, since this could be a breach
                raise PermissionDenied
            # TODO add error catching..
            c.validate(dct['op'], dct['val'])
            criteria.append(c)
        return criteria

    def _get_filters(self, criteria):
        filters = []
        for c in criteria:
            model = c.model_cls
            field_name = c.field_name
            operator = c.op_obj.operator
            value = c.val_obj
            is_negated = c.op_obj.is_negated
            path = []

            if self.model_tree.root_model != model:
                nodes = self.model_tree.path_to(model)
                path = self.model_tree.related_name_path(nodes)

            path.extend([field_name, operator])
            kwarg = {str('__'.join(path)): value}
            if is_negated:
                filters.append(~Q(**kwarg))
            else:
                filters.append(Q(**kwarg ))
        return filters

    def add_filters(self, queryset, pre_criteria):
        """Takes in a queryset and applies filters to it.
        TODO update to support OR's
        """
        criteria = self._get_criteria(pre_criteria)
        filters = self._get_filters(criteria)
        queryset = queryset.filter(*filters)
        return queryset

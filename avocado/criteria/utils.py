from django.db.models import Q

from avocado.concepts.utils import ConceptSet
from avocado.criteria.models import CriterionConcept
from avocado.criteria.cache import get_concept, get_concepts

def get_criteria(concept_ids, queryset=None):
    """Simple helper to retrieve an ordered list of criteria. Criteria that are
    not found are simply ignored.
    """
    concepts = []
    for concept in get_concepts(concept_ids, queryset):
        if concept is not None:
            concepts.append(concept)
    return concepts

class CriterionSet(ConceptSet):
    """Provides the mechanism to validate and normalize user-defined criteria.
    This interface provides the mechanisms to filter down a queryset.

    `pre_criteria' must be in the format:
        {<field_id>: {'op': u'foo', 'val': [u'11', u'39']}, ...}

    a dict with keys being the primary key of `Field' objects and the value
    being the choosen condition and params.

    The `queryset' must be provided as a starting point when fetching data
    about each criterion.
    """
    def __setstate__(self, dict_):
        queryset = CriterionConcept.objects.all()
        super(CriterionSet, self).__setstate__(dict_, queryset)

    def _get_filters(self, concepts):
        filters = []
        for concept in concepts:
            pass
        return filters

    def add_filters(self, queryset, pre_criteria):
        """Takes in a queryset and applies filters to it.
        TODO update to support OR's
        """
        criteria = self._get_criteria(pre_criteria)
        filters = self._get_filters(criteria)
        queryset = queryset.filter(*filters)
        return queryset

import cPickle as pickle

from django.test import TestCase

from avocado.modeltree import ModelTree
from avocado.criteria.models import Criterion
from avocado.criteria.utils import CriterionSet, get_criteria

__all__ = ('CriterionUtilsTestCase', 'CriterionSetTestCase')

class CriterionUtilsTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_get_criteria(self):
        cc1 = Criterion.objects.get(id=1)
        cc2 = Criterion.objects.get(id=2)

        criteria = get_criteria([1])
        self.assertEqual(criteria, [cc1])
        
        criteria = get_criteria([2, 1])
        self.assertEqual(criteria, [cc2, cc1])
        
        criteria = get_criteria([2, 3, 1])
        self.assertEqual(criteria, [cc2, cc1])


class CriterionSetTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        concepts = Criterion.objects.public()
        modeltree = ModelTree(Criterion)

        self.set = CriterionSet(concepts, modeltree)

    def test_pickling(self):
        from django.db import connection
        l1 = len(connection.queries)
        p = pickle.dumps(self.set)
        l2 = len(connection.queries)
        pickle.loads(p)
        l3 = len(connection.queries)

        self.assertEqual(l1, l2, l3)

from django.test import TestCase

from avocado.meta.utils import distribution
from avocado.tests import models

__all__ = ('DistributionTestCase',)

class DistributionTestCase(TestCase):
    fixtures = ['distribution_data.yaml']

    def setUp(self):
        self.title_qs = models.Title.objects.all().values_list('salary')

    def test_distribution_empty(self):
        # Test Empty queryset
        empty_title = self.title_qs.none()
        self.assertEqual(distribution(empty_title, 'salary', 'number'), [])

    def test_distribution_flat(self):
        # test flat queryset
        flat_qs = self.title_qs.filter(salary=15)
        self.assertEqual(distribution(flat_qs, 'salary', 'number'),
                [(15, 6)])

        self.assertEqual(distribution(self.title_qs, 'salary', 'number'),
                [(10, 1), (15, 6), (45, 1)])

    def test_distribution_one(self):
        # test queryset with 1 item
        one_qs = self.title_qs.filter(salary=45)
        self.assertEqual(distribution(one_qs, 'salary', 'number'),
                [(45, 1)])

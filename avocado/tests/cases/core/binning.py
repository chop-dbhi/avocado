from avocado.tests.base import BaseTestCase
from avocado.core.binning import distribution
from avocado.tests.models import Title

__all__ = ('DistributionTestCase',)

class DistributionTestCase(BaseTestCase):
    def setUp(self):
        self.title_qs = Title.objects.all().values_list('salary')

    def test_distribution_empty(self):
        # Test Empty queryset
        empty_title = self.title_qs.none()
        self.assertEqual(distribution(empty_title, 'salary', 'number'), [])

    def test_distribution_flat(self):
        self.assertEqual(distribution(self.title_qs.all(), 'salary', 'number'),
        	[(10000.0, 1), (200000.0, 1)])
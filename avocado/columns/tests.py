from django.test import TestCase

from avocado.modeltree import ModelTree
from avocado.columns import cache
from avocado.columns.models import ColumnConcept
from avocado.columns.utils import ColumnSet

__all__ = ('ColumnCachingTestCase',)

class ColumnCachingTestCase(TestCase):
    fixtures = ('test_data.yaml',)

    def test_get_concept(self):
        from django.core import cache as djcache
        
        concept_id = 1
        self.assertEqual(djcache.get(cache.COLUMN_CACHE_KEY % 1), None)
        
        concept = cache.get_concept(concept_id)
        self.assertEqual(djcache.get(cache.COLUMN_CACHE_KEY % 1), concept)

from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.columns.cache import cache
from avocado.models import ColumnConcept

__all__ = ('ColumnCacheTestCase',)

class ColumnCacheTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def setUp(self):
        djcache.clear()

    def test_get(self):
        concept_id = 1
        key = cache.CACHE_KEY % (ColumnConcept.__name__.lower(), concept_id)

        self.assertFalse(djcache.has_key(key))

        concept = cache.get(concept_id)
        self.assertNotEqual(concept, None)
        self.assertEqual(djcache.get(key), concept)

        djcache.delete(key)

        queryset = ColumnConcept.objects.none()
        concept = cache.get(concept_id, queryset=queryset)
        self.assertEqual(concept, None)
        self.assertFalse(djcache.has_key(key))

    def test_get_many(self):
        concept_ids = [1, 2]
        concepts = list(cache.get_many(concept_ids))

        self.assertEqual([x.id for x in concepts], concept_ids)
        for i, x in enumerate(concept_ids):
            key = cache.CACHE_KEY % (ColumnConcept.__name__.lower(), x)
            self.assertEqual(djcache.get(key), concepts[i])

    def test_get_fields(self):
        concept_id = 1
        key = cache.CACHE_KEY % (ColumnConcept.__name__.lower(), concept_id)
        fkey = cache.FIELD_CACHE_KEY % (ColumnConcept.__name__.lower(), concept_id)

        self.assertFalse(djcache.has_key(key))
        self.assertFalse(djcache.has_key(fkey))

        fields = cache.get_fields(concept_id)

        self.assertTrue(djcache.has_key(key))
        self.assertEqual(djcache.get(fkey), fields)

        self.assertEqual(cache.get_fields(3, ret_val=False), False)

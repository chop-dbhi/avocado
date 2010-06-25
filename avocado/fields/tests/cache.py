from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.fields import cache
from avocado.models import FieldConcept

__all__ = ('FieldCachingTestCase',)

class FieldCachingTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_get_concept(self):
        concept_id = 1
        key = cache.FIELD_CACHE_KEY % concept_id
        self.assertFalse(djcache.has_key(key))

        concept = cache.get_concept(concept_id)
        self.assertNotEqual(concept, None)
        self.assertEqual(djcache.get(key), concept)

        djcache.delete(key)

        queryset = FieldConcept.objects.none()
        concept = cache.get_concept(concept_id, queryset=queryset)
        self.assertEqual(concept, None)
        self.assertFalse(djcache.has_key(key))

    def test_get_concepts(self):
        concept_ids = [1, 2]
        concepts = list(cache.get_concepts(concept_ids))

        self.assertEqual([x.id for x in concepts], concept_ids)
        for i, x in enumerate(concept_ids):
            key = cache.FIELD_CACHE_KEY % x
            self.assertEqual(djcache.get(key), concepts[i])


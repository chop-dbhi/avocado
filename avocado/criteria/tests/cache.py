from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.criteria import cache
from avocado.models import CriterionConcept

__all__ = ('CriterionCachingTestCase',)

class CriterionCachingTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_get_concept(self):
        concept_id = 1
        key = cache.CRITERION_CACHE_KEY % concept_id
        self.assertFalse(djcache.has_key(key))

        concept = cache.get_concept(concept_id)
        self.assertNotEqual(concept, None)
        self.assertEqual(djcache.get(key), concept)

        djcache.delete(key)

        queryset = CriterionConcept.objects.none()
        concept = cache.get_concept(concept_id, queryset=queryset)
        self.assertEqual(concept, None)
        self.assertFalse(djcache.has_key(key))

    def test_get_concepts(self):
        concept_ids = [1, 2]
        concepts = list(cache.get_concepts(concept_ids))

        self.assertEqual([x.id for x in concepts], concept_ids)
        for i, x in enumerate(concept_ids):
            key = cache.CRITERION_CACHE_KEY % x
            self.assertEqual(djcache.get(key), concepts[i])

    def test_get_concept_fields(self):
        concept_id = 1
        key = cache.CRITERION_CACHE_KEY % concept_id
        fkey = cache.CRITERION_FIELD_CACHE_KEY % concept_id

        self.assertFalse(djcache.has_key(key))
        self.assertFalse(djcache.has_key(fkey))

        fields = cache.get_concept_fields(concept_id)

        self.assertTrue(djcache.has_key(key))
        self.assertEqual(djcache.get(fkey), fields)
        
        concept = CriterionConcept.objects.get(id=1)

        fields = cache.get_concept_fields(concept)

        self.assertTrue(djcache.has_key(key))
        self.assertEqual(djcache.get(fkey), fields)
        
        self.assertEqual(cache.get_concept_fields(3, ret_val=False), False)
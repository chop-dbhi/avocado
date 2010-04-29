import cPickle as pickle

from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.modeltree import ModelTree
from avocado.criteria import cache
from avocado.criteria.models import CriterionConcept
from avocado.criteria.utils import CriterionSet

__all__ = ('CriterionConceptSearchTestCase', 'CriterionCachingTestCase', 'CriterionSetTestCase')

class CriterionConceptTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def test_form_class(self):
        pass

class CriterionConceptSearchTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_fulltext(self):
        queryset1 = CriterionConcept.objects.fulltext_search('[)roc#ks')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_criterionconcept"."id" FROM "avocado_criterionconcept" WHERE search_tsv @@ to_tsquery(rocks) ORDER BY "avocado_criterionconcept"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = CriterionConcept.objects.fulltext_search('google< search *>')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_criterionconcept"."id" FROM "avocado_criterionconcept" WHERE search_tsv @@ to_tsquery(google&search) ORDER BY "avocado_criterionconcept"."name" ASC')
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = CriterionConcept.objects.fulltext_search('ca&$t1')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_criterionconcept"."id" FROM "avocado_criterionconcept" WHERE search_tsv @@ to_tsquery(cat1) ORDER BY "avocado_criterionconcept"."name" ASC')
        self.assertEqual(queryset3.count(), 2)

    def test_icontains(self):
        queryset1 = CriterionConcept.objects.icontains_search('pyt foo')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_criterionconcept"."id" FROM "avocado_criterionconcept" WHERE (UPPER("avocado_criterionconcept"."search_doc"::text) LIKE UPPER(%pyt%)  AND UPPER("avocado_criterionconcept"."search_doc"::text) LIKE UPPER(%foo%) ) ORDER BY "avocado_criterionconcept"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = CriterionConcept.objects.icontains_search('capab')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_criterionconcept"."id" FROM "avocado_criterionconcept" WHERE UPPER("avocado_criterionconcept"."search_doc"::text) LIKE UPPER(%capab%)  ORDER BY "avocado_criterionconcept"."name" ASC')
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = CriterionConcept.objects.icontains_search('cat')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_criterionconcept"."id" FROM "avocado_criterionconcept" WHERE UPPER("avocado_criterionconcept"."search_doc"::text) LIKE UPPER(%cat%)  ORDER BY "avocado_criterionconcept"."name" ASC')
        self.assertEqual(queryset3.count(), 2)


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


class CriterionSetTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        concepts = CriterionConcept.objects.public()
        modeltree = ModelTree(CriterionConcept)

        self.set = CriterionSet(concepts, modeltree)

    def test_pickling(self):
        from django.db import connection
        l1 = len(connection.queries)
        p = pickle.dumps(self.set)
        l2 = len(connection.queries)
        pickle.loads(p)
        l3 = len(connection.queries)

        self.assertEqual(l1, l2, l3)

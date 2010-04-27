import cPickle as pickle

from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.modeltree import ModelTree
from avocado.criteria import cache
from avocado.criteria.models import CriterionConcept
from avocado.criteria.utils import CriterionSet

__all__ = ('CriterionConceptSearchTestCase', 'CriterionCachingTestCase', 'CriterionSetTestCase')

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

    # def test_add_criteria(self):
    #     queryset1 = CriterionConcept.objects.all()
    #     concept_ids = [1]
    #     queryset2 = self.set.add_criteria(queryset1, concept_ids)
    # 
    #     self.assertEqual(str(queryset2.query), 'SELECT "avocado_criterionconcept"."id", "avocado_criterionconcept"."name", "avocado_criterionconcept"."keywords" FROM "avocado_criterionconcept" ORDER BY "avocado_criterionconcept"."name" ASC')
    # 
    #     concept_ids = [1, 2]
    #     queryset3 = self.set.add_criteria(queryset1, concept_ids)
    # 
    #     self.assertEqual(str(queryset3.query), 'SELECT "avocado_criterionconcept"."id", "avocado_criterionconcept"."name", "avocado_criterionconcept"."keywords", "avocado_fieldconcept"."name", "avocado_fieldconcept"."field_name" FROM "avocado_criterionconcept" LEFT OUTER JOIN "avocado_criterionconceptfield" ON ("avocado_criterionconcept"."id" = "avocado_criterionconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_criterionconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_criterionconcept"."name" ASC')
    # 
    # def test_add_ordering(self):
    #     queryset1 = CriterionConcept.objects.all()
    #     concept_orders = [(1, 'desc')]
    #     queryset2 = self.set.add_ordering(queryset1, concept_orders)
    # 
    #     self.assertEqual(str(queryset2.query), 'SELECT "avocado_criterionconcept"."id", "avocado_criterionconcept"."name", "avocado_criterionconcept"."description", "avocado_criterionconcept"."keywords", "avocado_criterionconcept"."category_id", "avocado_criterionconcept"."is_public", "avocado_criterionconcept"."order", "avocado_criterionconcept"."search_doc", "avocado_criterionconcept"."raw_formatter", "avocado_criterionconcept"."pretty_formatter" FROM "avocado_criterionconcept" ORDER BY "avocado_criterionconcept"."name" DESC, "avocado_criterionconcept"."keywords" DESC')
    # 
    #     concept_orders = [(2, 'desc'), (1, 'asc')]
    #     queryset3 = self.set.add_ordering(queryset1, concept_orders)
    # 
    #     self.assertEqual(str(queryset3.query), 'SELECT "avocado_criterionconcept"."id", "avocado_criterionconcept"."name", "avocado_criterionconcept"."description", "avocado_criterionconcept"."keywords", "avocado_criterionconcept"."category_id", "avocado_criterionconcept"."is_public", "avocado_criterionconcept"."order", "avocado_criterionconcept"."search_doc", "avocado_criterionconcept"."raw_formatter", "avocado_criterionconcept"."pretty_formatter" FROM "avocado_criterionconcept" LEFT OUTER JOIN "avocado_criterionconceptfield" ON ("avocado_criterionconcept"."id" = "avocado_criterionconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_criterionconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_criterionconcept"."name" ASC, "avocado_criterionconcept"."keywords" ASC')
    # 
    # def test_add_both(self):
    #     queryset1 = CriterionConcept.objects.all()
    # 
    #     concept_ids = [1]
    #     concept_orders = [(1, 'desc')]
    #     queryset2 = self.set.add_criteria(queryset1, concept_ids)
    #     queryset2 = self.set.add_ordering(queryset2, concept_orders)
    # 
    #     self.assertEqual(str(queryset2.query), 'SELECT "avocado_criterionconcept"."id", "avocado_criterionconcept"."name", "avocado_criterionconcept"."keywords" FROM "avocado_criterionconcept" ORDER BY "avocado_criterionconcept"."name" DESC, "avocado_criterionconcept"."keywords" DESC')
    # 
    #     queryset3 = self.set.add_ordering(queryset1, concept_orders)
    #     queryset3 = self.set.add_criteria(queryset3, concept_ids)
    # 
    #     self.assertEqual(str(queryset3.query), 'SELECT "avocado_criterionconcept"."id", "avocado_criterionconcept"."name", "avocado_criterionconcept"."keywords" FROM "avocado_criterionconcept" ORDER BY "avocado_criterionconcept"."name" DESC, "avocado_criterionconcept"."keywords" DESC')
    # 
    #     self.assertEqual(str(queryset2.query), str(queryset3.query))
    # 
    #     concept_ids = [2, 1]
    #     concept_orders = [(2, 'desc'), (1, 'asc')]
    #     queryset4 = self.set.add_criteria(queryset1, concept_ids)
    #     queryset4 = self.set.add_ordering(queryset4, concept_orders)
    # 
    #     self.assertEqual(str(queryset4.query), 'SELECT "avocado_criterionconcept"."id", "avocado_fieldconcept"."name", "avocado_fieldconcept"."field_name", "avocado_criterionconcept"."name", "avocado_criterionconcept"."keywords" FROM "avocado_criterionconcept" LEFT OUTER JOIN "avocado_criterionconceptfield" ON ("avocado_criterionconcept"."id" = "avocado_criterionconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_criterionconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_criterionconcept"."name" ASC, "avocado_criterionconcept"."keywords" ASC')
    # 
    #     queryset5 = self.set.add_ordering(queryset1, concept_orders)
    #     queryset5 = self.set.add_criteria(queryset5, concept_ids)
    # 
    #     self.assertEqual(str(queryset5.query), 'SELECT "avocado_criterionconcept"."id", "avocado_fieldconcept"."name", "avocado_fieldconcept"."field_name", "avocado_criterionconcept"."name", "avocado_criterionconcept"."keywords" FROM "avocado_criterionconcept" LEFT OUTER JOIN "avocado_criterionconceptfield" ON ("avocado_criterionconcept"."id" = "avocado_criterionconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_criterionconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_criterionconcept"."name" ASC, "avocado_criterionconcept"."keywords" ASC')
    # 
    #     self.assertEqual(str(queryset4.query), str(queryset5.query))

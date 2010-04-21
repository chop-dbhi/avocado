import cPickle as pickle

from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.modeltree import ModelTree
from avocado.columns import cache
from avocado.columns.models import ColumnConcept
from avocado.columns.utils import ColumnSet

__all__ = ('ColumnCachingTestCase', 'ColumnSetTestCase')

class ColumnCachingTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_get_concept(self):
        concept_id = 1
        key = cache.COLUMN_CACHE_KEY % concept_id
        self.assertFalse(djcache.has_key(key))
        
        concept = cache.get_concept(concept_id)
        self.assertNotEqual(concept, None)
        self.assertEqual(djcache.get(key), concept)
        
        djcache.delete(key)
        
        queryset = ColumnConcept.objects.none()
        concept = cache.get_concept(concept_id, queryset=queryset)
        self.assertEqual(concept, None)
        self.assertFalse(djcache.has_key(key))
    
    def test_get_concepts(self):
        concept_ids = [1, 2]
        concepts = list(cache.get_concepts(concept_ids))

        self.assertEqual([x.id for x in concepts], concept_ids)
        for i, x in enumerate(concept_ids):
            key = cache.COLUMN_CACHE_KEY % x
            self.assertEqual(djcache.get(key), concepts[i])

    def test_get_concept_fields(self):
        concept_id = 1
        key = cache.COLUMN_CACHE_KEY % concept_id
        fkey = cache.COLUMN_FIELD_CACHE_KEY % concept_id

        self.assertFalse(djcache.has_key(key))
        self.assertFalse(djcache.has_key(fkey))
        
        fields = cache.get_concept_fields(concept_id)
        
        self.assertTrue(djcache.has_key(key))
        self.assertEqual(djcache.get(fkey), fields)


class ColumnSetTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def setUp(self):
        concepts = ColumnConcept.objects.public()
        modeltree = ModelTree(ColumnConcept)

        self.set = ColumnSet(concepts, modeltree)
    
    def test_pickling(self):
        from django.db import connection
        l1 = len(connection.queries)
        p = pickle.dumps(self.set)
        l2 = len(connection.queries)
        set_ = pickle.loads(p)
        l3 = len(connection.queries)
        
        self.assertEqual(l1, l2, l3)
    
    def test_add_columns(self):
        queryset1 = ColumnConcept.objects.all()
        concept_ids = [1]
        queryset2 = self.set.add_columns(queryset1, concept_ids)
        
        self.assertEqual(str(queryset2.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."keywords" FROM "avocado_columnconcept" ORDER BY "avocado_columnconcept"."name" ASC')
        
        concept_ids = [1, 2]
        queryset3 = self.set.add_columns(queryset1, concept_ids)
        
        self.assertEqual(str(queryset3.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."keywords", "avocado_fieldconcept"."name", "avocado_fieldconcept"."field_name" FROM "avocado_columnconcept" LEFT OUTER JOIN "avocado_columnconceptfield" ON ("avocado_columnconcept"."id" = "avocado_columnconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_columnconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_columnconcept"."name" ASC')
        
    def test_add_ordering(self):
        queryset1 = ColumnConcept.objects.all()
        concept_orders = [(1, 'desc')]
        queryset2 = self.set.add_ordering(queryset1, concept_orders)
        
        self.assertEqual(str(queryset2.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."description", "avocado_columnconcept"."keywords", "avocado_columnconcept"."category_id", "avocado_columnconcept"."is_public", "avocado_columnconcept"."order", "avocado_columnconcept"."search_doc", "avocado_columnconcept"."raw_formatter", "avocado_columnconcept"."pretty_formatter" FROM "avocado_columnconcept" ORDER BY "avocado_columnconcept"."name" DESC, "avocado_columnconcept"."keywords" DESC')
        
        concept_orders = [(2, 'desc'), (1, 'asc')]
        queryset3 = self.set.add_ordering(queryset1, concept_orders)
        
        self.assertEqual(str(queryset3.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."description", "avocado_columnconcept"."keywords", "avocado_columnconcept"."category_id", "avocado_columnconcept"."is_public", "avocado_columnconcept"."order", "avocado_columnconcept"."search_doc", "avocado_columnconcept"."raw_formatter", "avocado_columnconcept"."pretty_formatter" FROM "avocado_columnconcept" LEFT OUTER JOIN "avocado_columnconceptfield" ON ("avocado_columnconcept"."id" = "avocado_columnconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_columnconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_columnconcept"."name" ASC, "avocado_columnconcept"."keywords" ASC')
    
    def test_add_both(self):
        queryset1 = ColumnConcept.objects.all()
        
        concept_ids = [1]
        concept_orders = [(1, 'desc')]
        queryset2 = self.set.add_columns(queryset1, concept_ids)
        queryset2 = self.set.add_ordering(queryset2, concept_orders)
        
        self.assertEqual(str(queryset2.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."keywords" FROM "avocado_columnconcept" ORDER BY "avocado_columnconcept"."name" DESC, "avocado_columnconcept"."keywords" DESC')
        
        queryset3 = self.set.add_ordering(queryset1, concept_orders)
        queryset3 = self.set.add_columns(queryset3, concept_ids)
        
        self.assertEqual(str(queryset3.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."keywords" FROM "avocado_columnconcept" ORDER BY "avocado_columnconcept"."name" DESC, "avocado_columnconcept"."keywords" DESC')
        
        self.assertEqual(str(queryset2.query), str(queryset3.query))

        concept_ids = [2, 1]
        concept_orders = [(2, 'desc'), (1, 'asc')]
        queryset4 = self.set.add_columns(queryset1, concept_ids)
        queryset4 = self.set.add_ordering(queryset4, concept_orders)
        
        self.assertEqual(str(queryset4.query), 'SELECT "avocado_columnconcept"."id", "avocado_fieldconcept"."name", "avocado_fieldconcept"."field_name", "avocado_columnconcept"."name", "avocado_columnconcept"."keywords" FROM "avocado_columnconcept" LEFT OUTER JOIN "avocado_columnconceptfield" ON ("avocado_columnconcept"."id" = "avocado_columnconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_columnconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_columnconcept"."name" ASC, "avocado_columnconcept"."keywords" ASC')
        
        queryset5 = self.set.add_ordering(queryset1, concept_orders)
        queryset5 = self.set.add_columns(queryset5, concept_ids)
        
        self.assertEqual(str(queryset5.query), 'SELECT "avocado_columnconcept"."id", "avocado_fieldconcept"."name", "avocado_fieldconcept"."field_name", "avocado_columnconcept"."name", "avocado_columnconcept"."keywords" FROM "avocado_columnconcept" LEFT OUTER JOIN "avocado_columnconceptfield" ON ("avocado_columnconcept"."id" = "avocado_columnconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_columnconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_columnconcept"."name" ASC, "avocado_columnconcept"."keywords" ASC')
        
        self.assertEqual(str(queryset4.query), str(queryset5.query))
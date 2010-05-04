import cPickle as pickle
from copy import deepcopy

from django.test import TestCase
from django.core.cache import cache as djcache

from avocado.modeltree import ModelTree
from avocado.columns import cache
from avocado.columns.models import ColumnConcept
from avocado.columns.utils import ColumnSet
from avocado.columns.formatters import (JSONFormatterLibrary, FormatterLibrary,
    RegisterError)

__all__ = ('ColumnConceptSearchTestCase', 'ColumnCachingTestCase',
    'ColumnSetTestCase', 'FormatterLibraryTestCase', 'JSONFormatterLibraryTestCase')

class ColumnConceptSearchTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_fulltext(self):
        queryset1 = ColumnConcept.objects.fulltext_search('[)roc#ks')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_columnconcept"."id" FROM "avocado_columnconcept" WHERE search_tsv @@ to_tsquery(rocks) ORDER BY "avocado_columnconcept"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = ColumnConcept.objects.fulltext_search('google< search *>')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_columnconcept"."id" FROM "avocado_columnconcept" WHERE search_tsv @@ to_tsquery(google&search) ORDER BY "avocado_columnconcept"."name" ASC')
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = ColumnConcept.objects.fulltext_search('ca&$t1')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_columnconcept"."id" FROM "avocado_columnconcept" WHERE search_tsv @@ to_tsquery(cat1) ORDER BY "avocado_columnconcept"."name" ASC')
        self.assertEqual(queryset3.count(), 2)

    def test_icontains(self):
        queryset1 = ColumnConcept.objects.icontains_search('pyt foo')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_columnconcept"."id" FROM "avocado_columnconcept" WHERE (UPPER("avocado_columnconcept"."search_doc"::text) LIKE UPPER(%pyt%)  AND UPPER("avocado_columnconcept"."search_doc"::text) LIKE UPPER(%foo%) ) ORDER BY "avocado_columnconcept"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = ColumnConcept.objects.icontains_search('capab')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_columnconcept"."id" FROM "avocado_columnconcept" WHERE UPPER("avocado_columnconcept"."search_doc"::text) LIKE UPPER(%capab%)  ORDER BY "avocado_columnconcept"."name" ASC')
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = ColumnConcept.objects.icontains_search('cat')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_columnconcept"."id" FROM "avocado_columnconcept" WHERE UPPER("avocado_columnconcept"."search_doc"::text) LIKE UPPER(%cat%)  ORDER BY "avocado_columnconcept"."name" ASC')
        self.assertEqual(queryset3.count(), 2)


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
        pickle.loads(p)
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

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."description", "avocado_columnconcept"."keywords", "avocado_columnconcept"."category_id", "avocado_columnconcept"."is_public", "avocado_columnconcept"."order", "avocado_columnconcept"."search_doc" FROM "avocado_columnconcept" ORDER BY "avocado_columnconcept"."name" DESC, "avocado_columnconcept"."keywords" DESC')

        concept_orders = [(2, 'desc'), (1, 'asc')]
        queryset3 = self.set.add_ordering(queryset1, concept_orders)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_columnconcept"."id", "avocado_columnconcept"."name", "avocado_columnconcept"."description", "avocado_columnconcept"."keywords", "avocado_columnconcept"."category_id", "avocado_columnconcept"."is_public", "avocado_columnconcept"."order", "avocado_columnconcept"."search_doc" FROM "avocado_columnconcept" LEFT OUTER JOIN "avocado_columnconceptfield" ON ("avocado_columnconcept"."id" = "avocado_columnconceptfield"."concept_id") LEFT OUTER JOIN "avocado_fieldconcept" ON ("avocado_columnconceptfield"."field_id" = "avocado_fieldconcept"."id") ORDER BY "avocado_fieldconcept"."name" DESC, "avocado_fieldconcept"."field_name" DESC, "avocado_columnconcept"."name" ASC, "avocado_columnconcept"."keywords" ASC')

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


class FormatterLibraryTestCase(TestCase):
    def setUp(self):
        super(FormatterLibraryTestCase, self).setUp()
        self.library = FormatterLibrary()

    def test_no_formatters(self):
        rows = [
            (4, None, 'foo', set([3,4,5]), 129),
            (10, 29, 'foo', [3,4,5], False),
            (None, 'bar', 'foo', None, True),
        ]
        
        rows1 = list(self.library.format(rows, [(None, 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(rows1, [
            ('4 None', 'foo set([3, 4, 5])', 129),
            ('10 29', 'foo [3, 4, 5]', False),
            ('None bar', 'foo None', True),
        ])
        
        rows2 = list(self.library.format(rows, [(0, 1), ('afunc', 3)],
            idx=(1, None)))
        
        self.assertEqual(rows2, [
            (4, 'None', 'foo set([3, 4, 5]) 129'),
            (10, '29', 'foo [3, 4, 5] False'),
            (None,  'bar', 'foo None True'),
        ])

        # if an 'empty' rule is provided, it is skipped
        rows3 = list(self.library.format(rows, [(None, 0), ('afunc', 2)],
            idx=(1, None)))
        
        self.assertEqual(rows3, [
            (4, 'None foo'),
            (10, '29 foo'),
            (None, 'bar foo'),
        ])

    def test_register(self):
        @self.library.register
        def func1(arg1, arg2):
            return arg1 + arg2
        
        self.assertEqual(func1(5, 5), self.library.get('func1')(5, 5))
        
        @self.library.register('foo bar')
        def func2(arg1):
            return '%s is a cool arg' % arg1
        
        self.assertEqual(func2(5), self.library.get('func2')(5))

        @self.library.register('boolean')
        def func3(arg1):
            return arg1 and 'Yes' or 'No'

        self.assertEqual(func3(None), self.library.get('func3')(None))
        
        def func3(arg1):
            return
        
        self.assertRaises(RegisterError, self.library.register('another'), func3)

    def test_formatters(self):
        self.test_register()
        
        rows = [
            (4, None, 'foo', set([3,4,5]), 129),
            (10, 29, 'foo', [3,4,5], False),
            (None, 'bar', 'foo', None, True),
        ]
        
        rows1 = list(self.library.format(rows, [('func1', 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(rows1, [
            ('(data format error)', 'foo set([3, 4, 5])', 129),
            (39, 'foo [3, 4, 5]', False),
            ('(data format error)', 'foo None', True),
        ])
        
        rows2 = list(self.library.format(rows, [('func2', 1), ('', 2), ('func3', 1)],
            idx=(1, None)))
        
        self.assertEqual(rows2, [
            (4, 'None is a cool arg', 'foo set([3, 4, 5])', 'Yes'),
            (10, '29 is a cool arg', 'foo [3, 4, 5]',  'No'),
            (None,  'bar is a cool arg', 'foo None', 'Yes'),
        ])


class JSONFormatterLibraryTestCase(TestCase):
    def setUp(self):
        super(JSONFormatterLibraryTestCase, self).setUp()
        self.library = JSONFormatterLibrary()

    def test_no_formatters(self):
        data = [
            {'id': 1, 'data': (4, None, 'foo', set([3,4,5]), 129)},
            {'id': 2, 'data': (10, 29, 'foo', [3,4,5], False)},
            {'id': 3, 'data': (None, 'bar', 'foo', None, True)},
        ]
        
        data1 = list(self.library.format(deepcopy(data), [(None, 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(data1, [
            {'id': 1, 'data': ('4 None', 'foo set([3, 4, 5])', 129)},
            {'id': 2, 'data': ('10 29', 'foo [3, 4, 5]', False)},
            {'id': 3, 'data': ('None bar', 'foo None', True)},
        ])
        
        data2 = list(self.library.format(deepcopy(data), [(0, 1), ('afunc', 3)],
            idx=(1, None)))
        
        self.assertEqual(data2, [
            {'id': 1, 'data': (4, 'None', 'foo set([3, 4, 5]) 129')},
            {'id': 2, 'data': (10, '29', 'foo [3, 4, 5] False')},
            {'id': 3, 'data': (None,  'bar', 'foo None True')},
        ])

        # if an 'empty' rule is provided, it is skipped
        data3 = list(self.library.format(deepcopy(data), [(None, 0), ('afunc', 2)],
            idx=(1, None)))
        
        self.assertEqual(data3, [
            {'id': 1, 'data': (4, 'None foo')},
            {'id': 2, 'data': (10, '29 foo')},
            {'id': 3, 'data': (None, 'bar foo')},
        ])

    def test_register(self):
        @self.library.register
        def func1(arg1, arg2):
            return arg1 + arg2
        
        self.assertEqual(func1(5, 5), self.library.get('func1')(5, 5))
        
        @self.library.register('foo bar')
        def func2(arg1):
            return '%s is a cool arg' % arg1
        
        self.assertEqual(func2(5), self.library.get('func2')(5))

        @self.library.register('boolean')
        def func3(arg1):
            return arg1 and 'Yes' or 'No'

        self.assertEqual(func3(None), self.library.get('func3')(None))
        
        def func3(arg1):
            return
        
        self.assertRaises(RegisterError, self.library.register('another'), func3)

    def test_formatters(self):
        self.test_register()
        
        data = [
            {'id': 1, 'data': (4, None, 'foo', set([3,4,5]), 129)},
            {'id': 2, 'data': (10, 29, 'foo', [3,4,5], False)},
            {'id': 3, 'data': (None, 'bar', 'foo', None, True)},
        ]
        
        data1 = list(self.library.format(deepcopy(data), [('func1', 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(data1, [
            {'id': 1, 'data': ('<span class="data-format-error">(data format error)</span>', 'foo set([3, 4, 5])', 129)},
            {'id': 2, 'data': (39, 'foo [3, 4, 5]', False)},
            {'id': 3, 'data': ('<span class="data-format-error">(data format error)</span>', 'foo None', True)},
        ])
        
        data2 = list(self.library.format(deepcopy(data), [('func2', 1), ('', 2), ('func3', 1)],
            idx=(1, None), key='data'))
        
        self.assertEqual(data2, [
            {'id': 1, 'data': (4, 'None is a cool arg', 'foo set([3, 4, 5])', 'Yes')},
            {'id': 2, 'data': (10, '29 is a cool arg', 'foo [3, 4, 5]',  'No')},
            {'id': 3, 'data': (None,  'bar is a cool arg', 'foo None', 'Yes')},
        ])
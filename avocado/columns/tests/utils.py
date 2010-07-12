import cPickle as pickle

from django.test import TestCase

from avocado.columns.models import ColumnConcept
from avocado.columns.utils import ColumnSet, get_columns, get_column_orders

__all__ = ('ColumnUtilsTestCase', 'ColumnSetTestCase')


class ColumnUtilsTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_get_columns(self):
        cc1 = ColumnConcept.objects.get(id=1)
        cc2 = ColumnConcept.objects.get(id=2)

        columns = get_columns([1])
        self.assertEqual(columns, [cc1])

        columns = get_columns([2, 1])
        self.assertEqual(columns, [cc2, cc1])

        columns = get_columns([2, 3, 1])
        self.assertEqual(columns, [cc2, cc1])

    def test_get_column_orders(self):
        cc1 = ColumnConcept.objects.get(id=1)
        cc2 = ColumnConcept.objects.get(id=2)

        column_orders = get_column_orders([(1, 'desc')])
        self.assertEqual(column_orders, {cc1:
            {'direction': 'desc', 'order': 0}
        })

        column_orders = get_column_orders([(2, 'asc'), (1, 'desc')])
        self.assertEqual(column_orders, {
            cc1: {'direction': 'desc', 'order': 1},
            cc2: {'direction': 'asc', 'order': 0},
        })


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



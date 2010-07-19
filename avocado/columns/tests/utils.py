import cPickle as pickle

from django.test import TestCase

from avocado.modeltree import ModelTree
from avocado.columns.models import Column
from avocado.columns.utils import ColumnSet, get_columns, get_column_orders

__all__ = ('ColumnUtilsTestCase', 'ColumnSetTestCase')

class ColumnUtilsTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_get_columns(self):
        cc1 = Column.objects.get(id=1)
        cc2 = Column.objects.get(id=2)

        columns = get_columns([1])
        self.assertEqual(columns, [cc1])

        columns = get_columns([2, 1])
        self.assertEqual(columns, [cc2, cc1])

        columns = get_columns([2, 3, 1])
        self.assertEqual(columns, [cc2, cc1])

    def test_get_column_orders(self):
        cc1 = Column.objects.get(id=1)
        cc2 = Column.objects.get(id=2)

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
        concepts = Column.objects.public()
        modeltree = ModelTree(Column)

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
        queryset1 = Column.objects.all()
        concept_ids = [1]
        queryset2 = self.set.add_columns(queryset1, concept_ids)

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" ORDER BY "avocado_column"."name" ASC')

        concept_ids = [1, 2]
        queryset3 = self.set.add_columns(queryset1, concept_ids)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords", "avocado_modelfield"."name", "avocado_modelfield"."field_name" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_column"."name" ASC')

    def test_add_ordering(self):
        queryset1 = Column.objects.all()
        concept_orders = [(1, 'desc')]
        queryset2 = self.set.add_ordering(queryset1, concept_orders)

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."description", "avocado_column"."keywords", "avocado_column"."category_id", "avocado_column"."is_public", "avocado_column"."order", "avocado_column"."search_doc" FROM "avocado_column" ORDER BY "avocado_column"."name" DESC, "avocado_column"."keywords" DESC')

        concept_orders = [(2, 'desc'), (1, 'asc')]
        queryset3 = self.set.add_ordering(queryset1, concept_orders)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."description", "avocado_column"."keywords", "avocado_column"."category_id", "avocado_column"."is_public", "avocado_column"."order", "avocado_column"."search_doc" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_modelfield"."name" DESC, "avocado_modelfield"."field_name" DESC, "avocado_column"."name" ASC, "avocado_column"."keywords" ASC')

    def test_add_both(self):
        queryset1 = Column.objects.all()

        concept_ids = [1]
        concept_orders = [(1, 'desc')]
        queryset2 = self.set.add_columns(queryset1, concept_ids)
        queryset2 = self.set.add_ordering(queryset2, concept_orders)

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" ORDER BY "avocado_column"."name" DESC, "avocado_column"."keywords" DESC')

        queryset3 = self.set.add_ordering(queryset1, concept_orders)
        queryset3 = self.set.add_columns(queryset3, concept_ids)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" ORDER BY "avocado_column"."name" DESC, "avocado_column"."keywords" DESC')

        self.assertEqual(str(queryset2.query), str(queryset3.query))

        concept_ids = [2, 1]
        concept_orders = [(2, 'desc'), (1, 'asc')]
        queryset4 = self.set.add_columns(queryset1, concept_ids)
        queryset4 = self.set.add_ordering(queryset4, concept_orders)

        self.assertEqual(str(queryset4.query), 'SELECT "avocado_column"."id", "avocado_modelfield"."name", "avocado_modelfield"."field_name", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_modelfield"."name" DESC, "avocado_modelfield"."field_name" DESC, "avocado_column"."name" ASC, "avocado_column"."keywords" ASC')

        queryset5 = self.set.add_ordering(queryset1, concept_orders)
        queryset5 = self.set.add_columns(queryset5, concept_ids)

        self.assertEqual(str(queryset5.query), 'SELECT "avocado_column"."id", "avocado_modelfield"."name", "avocado_modelfield"."field_name", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_modelfield"."name" DESC, "avocado_modelfield"."field_name" DESC, "avocado_column"."name" ASC, "avocado_column"."keywords" ASC')

        self.assertEqual(str(queryset4.query), str(queryset5.query))



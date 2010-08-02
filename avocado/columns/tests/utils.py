from django.test import TestCase
from django.core.cache import cache as dcache

from avocado.modeltree import DEFAULT_MODELTREE
from avocado.columns.models import Column
from avocado.columns import utils
from avocado.columns.cache import cache

__all__ = ('ColumnUtilsTestCase',)

class ColumnUtilsTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def test_add_columns(self):
        queryset1 = Column.objects.all()
        columns = cache.get_many([1])
        queryset2 = utils.add_columns(queryset1, columns, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" ORDER BY "avocado_column"."name" ASC')

        columns = cache.get_many([1, 2])
        queryset3 = utils.add_columns(queryset1, columns, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords", "avocado_modelfield"."name", "avocado_modelfield"."field_name" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_column"."name" ASC')

    def test_add_ordering(self):
        queryset1 = Column.objects.values('id')
        column_orders = [(cache.get(x), y) for x, y in [(1, 'desc')]]
        queryset2 = utils.add_ordering(queryset1, column_orders, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_column"."id" FROM "avocado_column" ORDER BY "avocado_column"."name" DESC, "avocado_column"."keywords" DESC')

        column_orders = [(cache.get(x), y) for x, y in [(2, 'desc'), (1, 'asc')]]
        queryset3 = utils.add_ordering(queryset1, column_orders, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_column"."id" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_modelfield"."name" DESC, "avocado_modelfield"."field_name" DESC, "avocado_column"."name" ASC, "avocado_column"."keywords" ASC')

    def test_add_both(self):
        queryset1 = Column.objects.all()

        columns = cache.get_many([1])
        column_orders = [(cache.get(x), y) for x, y in [(1, 'desc')]]
        
        queryset2 = utils.add_columns(queryset1, columns, DEFAULT_MODELTREE)
        queryset2 = utils.add_ordering(queryset2, column_orders, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset2.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" ORDER BY "avocado_column"."name" DESC, "avocado_column"."keywords" DESC')

        queryset3 = utils.add_ordering(queryset1, column_orders, DEFAULT_MODELTREE)
        queryset3 = utils.add_columns(queryset3, columns, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset3.query), 'SELECT "avocado_column"."id", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" ORDER BY "avocado_column"."name" DESC, "avocado_column"."keywords" DESC')

        self.assertEqual(str(queryset2.query), str(queryset3.query))

        columns = cache.get_many([2, 1])
        column_orders = [(cache.get(x), y) for x, y in [(2, 'desc'), (1, 'asc')]]
        queryset4 = utils.add_columns(queryset1, columns, DEFAULT_MODELTREE)
        queryset4 = utils.add_ordering(queryset4, column_orders, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset4.query), 'SELECT "avocado_column"."id", "avocado_modelfield"."name", "avocado_modelfield"."field_name", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_modelfield"."name" DESC, "avocado_modelfield"."field_name" DESC, "avocado_column"."name" ASC, "avocado_column"."keywords" ASC')

        queryset5 = utils.add_ordering(queryset1, column_orders, DEFAULT_MODELTREE)
        queryset5 = utils.add_columns(queryset5, columns, DEFAULT_MODELTREE)

        self.assertEqual(str(queryset5.query), 'SELECT "avocado_column"."id", "avocado_modelfield"."name", "avocado_modelfield"."field_name", "avocado_column"."name", "avocado_column"."keywords" FROM "avocado_column" LEFT OUTER JOIN "avocado_columnfield" ON ("avocado_column"."id" = "avocado_columnfield"."concept_id") LEFT OUTER JOIN "avocado_modelfield" ON ("avocado_columnfield"."field_id" = "avocado_modelfield"."id") ORDER BY "avocado_modelfield"."name" DESC, "avocado_modelfield"."field_name" DESC, "avocado_column"."name" ASC, "avocado_column"."keywords" ASC')

        self.assertEqual(str(queryset4.query), str(queryset5.query))
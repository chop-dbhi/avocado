from django.test import TestCase
from django.contrib.auth.models import User

from avocado.columns.models import Column

__all__ = ('ColumnSearchTestCase',)

class ColumnSearchTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_fulltext(self):
        queryset1 = Column.objects.fulltext_search('[)roc#ks')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_column"."id" FROM "avocado_column" WHERE "avocado_column"."search_tsv" @@ to_tsquery(rocks) ORDER BY "avocado_column"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = Column.objects.fulltext_search('google< search *>')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_column"."id" FROM "avocado_column" WHERE "avocado_column"."search_tsv" @@ to_tsquery(google&search) ORDER BY "avocado_column"."name" ASC')
        self.assertEqual(queryset2.count(), 3)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = Column.objects.fulltext_search('ca&$t1')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_column"."id" FROM "avocado_column" WHERE "avocado_column"."search_tsv" @@ to_tsquery(cat1) ORDER BY "avocado_column"."name" ASC')
        self.assertEqual(queryset3.count(), 4)

    def test_icontains(self):
        queryset1 = Column.objects.icontains_search('pyt foo')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_column"."id" FROM "avocado_column" WHERE (UPPER("avocado_column"."search_doc"::text) LIKE UPPER(%pyt%)  AND UPPER("avocado_column"."search_doc"::text) LIKE UPPER(%foo%) ) ORDER BY "avocado_column"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = Column.objects.icontains_search('capab')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_column"."id" FROM "avocado_column" WHERE UPPER("avocado_column"."search_doc"::text) LIKE UPPER(%capab%)  ORDER BY "avocado_column"."name" ASC')
        self.assertEqual(queryset2.count(), 3)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = Column.objects.icontains_search('cat')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_column"."id" FROM "avocado_column" WHERE UPPER("avocado_column"."search_doc"::text) LIKE UPPER(%cat%)  ORDER BY "avocado_column"."name" ASC')
        self.assertEqual(queryset3.count(), 4)

    def test_public(self):
        public_objects = Column.objects.public()
        self.assertEqual(public_objects.count(), 2)
        self.assertEqual(list(public_objects.values_list('id', flat=True)), [2, 3])

    def test_restricted(self):
        user = User.objects.get(pk=1)
        restricted_objects = Column.objects.public(user)
        self.assertEqual(restricted_objects.count(), 2)
        self.assertEqual(list(restricted_objects.values_list('id', flat=True)), [2, 3])


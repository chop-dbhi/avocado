from django.test import TestCase

from avocado.columns.models import ColumnConcept

__all__ = ('ColumnConceptSearchTestCase',)

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




from django.test import TestCase

from avocado.criteria.models import Criterion

__all__ = ('CriterionSearchTestCase',)

class CriterionSearchTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_fulltext(self):
        queryset1 = Criterion.objects.fulltext_search('[)roc#ks')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_criterion"."id" FROM "avocado_criterion" WHERE search_tsv @@ to_tsquery(rocks) ORDER BY "avocado_criterion"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = Criterion.objects.fulltext_search('google< search *>')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_criterion"."id" FROM "avocado_criterion" WHERE search_tsv @@ to_tsquery(google&search) ORDER BY "avocado_criterion"."name" ASC')
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = Criterion.objects.fulltext_search('ca&$t1')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_criterion"."id" FROM "avocado_criterion" WHERE search_tsv @@ to_tsquery(cat1) ORDER BY "avocado_criterion"."name" ASC')
        self.assertEqual(queryset3.count(), 2)

    def test_icontains(self):
        queryset1 = Criterion.objects.icontains_search('pyt foo')
        self.assertEqual(str(queryset1.values('id').query), 'SELECT "avocado_criterion"."id" FROM "avocado_criterion" WHERE (UPPER("avocado_criterion"."search_doc"::text) LIKE UPPER(%pyt%)  AND UPPER("avocado_criterion"."search_doc"::text) LIKE UPPER(%foo%) ) ORDER BY "avocado_criterion"."name" ASC')
        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset1[0].id, 1)

        queryset2 = Criterion.objects.icontains_search('capab')
        self.assertEqual(str(queryset2.values('id').query), 'SELECT "avocado_criterion"."id" FROM "avocado_criterion" WHERE UPPER("avocado_criterion"."search_doc"::text) LIKE UPPER(%capab%)  ORDER BY "avocado_criterion"."name" ASC')
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset2[0].id, 2)

        queryset3 = Criterion.objects.icontains_search('cat')
        self.assertEqual(str(queryset3.values('id').query), 'SELECT "avocado_criterion"."id" FROM "avocado_criterion" WHERE UPPER("avocado_criterion"."search_doc"::text) LIKE UPPER(%cat%)  ORDER BY "avocado_criterion"."name" ASC')
        self.assertEqual(queryset3.count(), 2)




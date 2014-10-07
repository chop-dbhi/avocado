from django.test import TestCase
from avocado.models import DataField, DataConcept, DataConceptField, DataView
from ...models import Month


class LexiconTestCase(TestCase):
    fixtures = ['month_data.json']

    def test_datafield(self):
        f = DataField(app_name='tests', model_name='month', field_name='id')
        self.assertEqual(f.values(), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
        self.assertEqual(
            f.labels(),
            (u'January', u'February', u'March', u'April', u'May', u'June',
             u'July', u'August', u'September', u'October', u'November',
             u'December'))
        self.assertEqual(f.codes(), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    def test_foreign_key_datafield(self):
        f = DataField(app_name='tests', model_name='date', field_name='month')
        self.assertEqual(f.model, Month)
        self.assertEqual(f.field, Month._meta.pk)
        self.assertEqual(f.values(), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
        self.assertEqual(
            f.labels(),
            (u'January', u'February', u'March', u'April', u'May', u'June',
             u'July', u'August', u'September', u'October', u'November',
             u'December'))
        self.assertEqual(f.codes(), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    def test_dataview_order_by(self):
        f = DataField(app_name='tests', model_name='month', field_name='id')
        f.save()

        c = DataConcept()
        c.save()

        cf = DataConceptField(field=f, concept=c)
        cf.save()

        v = DataView({'ordering': [[c.pk, 'asc']]})

        qs = Month.objects.filter(label__startswith='J').values('id')
        self.assertEqual(
            unicode(v.apply(qs).query),
            'SELECT "tests_month"."id" FROM "tests_month" WHERE '
            '"tests_month"."label" LIKE J% ESCAPE \'\\\'  ORDER BY '
            '"tests_month"."order" ASC')

    def test_dist(self):
        f = DataField(app_name='tests', model_name='date', field_name='month')
        # Months of the year
        result = tuple([(i, 1) for i in range(1, 13)])
        self.assertEqual(f.dist(), result)

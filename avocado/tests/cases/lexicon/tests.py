from django.test import TestCase
from avocado.models import DataField, DataConcept, DataConceptField, DataView
from .models import Month


class LexiconTestCase(TestCase):
    fixtures = ['lexicon.json']

    def test_datafield_properties(self):
        f = DataField(app_name='lexicon', model_name='month', field_name='value')
        self.assertEqual(f.values, (u'jan', u'feb', u'mar', u'apr', u'may', u'jun', u'jul', u'aug', u'sep', u'oct', u'nov', u'dec'))
        self.assertEqual(f.labels, (u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August', u'September', u'October', u'November', u'December'))
        self.assertEqual(f.codes, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    def test_dataview_order_by(self):
        f = DataField(app_name='lexicon', model_name='month', field_name='value')
        f.save()

        c = DataConcept()
        c.save()

        cf = DataConceptField(field=f, concept=c)
        cf.save()

        v = DataView({'ordering': [c.pk]})

        qs = Month.objects.filter(label__startswith='J').values('id')
        self.assertEqual(str(v.apply(qs).query), 'SELECT "lexicon_month"."id" FROM "lexicon_month" WHERE "lexicon_month"."label" LIKE J% ESCAPE \'\\\'  ORDER BY "lexicon_month"."order" ASC')

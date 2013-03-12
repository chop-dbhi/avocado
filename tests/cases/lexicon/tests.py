from django.test import TestCase
from avocado.models import DataField
from .models import Month


class LexiconTestCase(TestCase):
    fixtures = ['lexicon.json']

    def test_interface(self):
        f = DataField(app_name='lexicon', model_name='month', field_name='id')
        i = f._interface

        self.assertEqual(i.model, Month)

        self.assertEqual(i.field, Month._meta.pk)
        self.assertEqual(i._value_field.name, Month._meta.pk.name)

        self.assertEqual(i._label_field.name, 'label')
        self.assertEqual(i._search_field.name, 'label')

        self.assertEqual(i._order_field.name, 'order')
        self.assertEqual(i._code_field.name, 'code')

        self.assertEqual(list(i.values()), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(list(i.labels()), [u'January', u'February', u'March',
            u'April', u'May', u'June', u'July', u'August', u'September',
            u'October', u'November', u'December'])
        self.assertEqual(list(i.codes()), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    def test_interface_foreign_key(self):
        f = DataField(app_name='lexicon', model_name='date', field_name='month')

        self.assertEqual(f._interface.model, Month)
        self.assertEqual(f._interface.field, Month._meta.pk)

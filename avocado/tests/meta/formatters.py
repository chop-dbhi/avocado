from django.test import TestCase
from avocado.meta.formatters import Formatter
from django.core.management import call_command
from avocado.meta.models import Field, Concept, ConceptField
from avocado.tests import models

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class FormatterTestCase(TestCase):
    fixtures = ['format_data.yaml']

    def setUp(self):
        self.f = Formatter()
        call_command('avocado', 'sync', 'tests', verbosity=0)


        title_def = Field.objects.get_by_natural_key('tests',
            'title', 'name')
        salary_def = Field.objects.get_by_natural_key('tests',
            'title', 'salary')
        boss_def = Field.objects.get_by_natural_key('tests',
            'title', 'boss')

        self.c = Concept()
        self.c.name = "title"
        self.c.save()

        ConceptField(concept=self.c,
                field=title_def, order=1).save()
        ConceptField(concept=self.c,
                field=salary_def, order=2).save()
        ConceptField(concept=self.c,
                field=boss_def, order=3).save()

        self.values = OrderedDict({
            'title': {
                'name': 'Title',
                'value': 'CEO',
                'field': title_def,
            },
            'salary': {
                'name': 'Salary',
                'value': 100000,
                'field': salary_def,
            },
            'boss': {
                'name': 'Boss?',
                'value': True,
                'field': boss_def,
            },
        })

        self.f = Formatter()

    def test_to_string(self):
        to_string = self.f.to_string
        values = self.values['title']
        # test a string
        string = to_string(values['name'], values['value'],
                values['field'], self.c)
        self.assertEqual(string, 'CEO')

        values = self.values['salary']
        str_num = to_string(values['name'], values['value'],
                values['field'], self.c)
        self.assertEqual(str_num, '100000')

        values = self.values['boss']
        bool_num = to_string(values['name'], values['value'],
                values['field'], self.c)
        self.assertEqual(bool_num, 'True')

    def test_to_number(self):
        to_num = self.f.to_number
        values = self.values['salary']
        num = to_num(values['name'], values['value'],
                values['field'], self.c)
        self.assertEqual(num, 100000)

        values = self.values['boss']
        bool_num = to_num(values['name'], values['value'],
                values['field'], self.c)
        self.assertEqual(bool_num, 1)

        values = self.values['title']
        self.assertRaises(Exception, to_num, values['name'], values['value'],
                values['field'], self.c)

    def test_to_bool(self):
        to_bool = self.f.to_bool
        values = self.values['boss']
        bool_str = to_bool(values['name'], values['value'],
                values['field'], self.c)
        self.assertEqual(bool_str, True)

        values = self.values['title']
        self.assertRaises(Exception, to_bool, values['name'], values['value'],
                values['field'], self.c)

        values = self.values['salary']
        self.assertRaises(Exception, to_bool, values['name'], values['value'],
                values['field'], self.c)

    def test_to_coded(self):
        to_coded = self.f.to_coded
        values = self.values['boss']
        bool_convert = to_coded(values['name'], values['value'],
            values['field'], self.c)
        self.assertTrue(bool_convert, 1)

        values = self.values['title']
        self.assertRaises(Exception, to_coded, values['name'], values['value'],
                values['field'], self.c)


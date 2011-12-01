from django.test import TestCase
from avocado.meta.formatters import Formatter
from django.core.management import call_command
from avocado.meta.models import Field, Concept, ConceptField
from avocado.tests import models

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

__all__ = ('FormatterTestCase',)

class FormatterTestCase(TestCase):
    fixtures = ['format_data.yaml']

    def setUp(self):
        call_command('avocado', 'sync', 'tests', verbosity=0)


        title_field = Field.objects.get_by_natural_key('tests',
            'title', 'name')
        salary_field = Field.objects.get_by_natural_key('tests',
            'title', 'salary')
        boss_field = Field.objects.get_by_natural_key('tests',
            'title', 'boss')

        self.c = Concept()
        self.c.name = "title"
        self.c.save()

        ConceptField(concept=self.c, field=title_field, order=1).save()
        ConceptField(concept=self.c, field=salary_field, order=2).save()
        ConceptField(concept=self.c, field=boss_field, order=3).save()

        self.values = OrderedDict({
            'title': {
                'name': 'Title',
                'value': 'CEO',
                'field': title_field,
            },
            'salary': {
                'name': 'Salary',
                'value': 100000,
                'field': salary_field,
            },
            'boss': {
                'name': 'Boss?',
                'value': True,
                'field': boss_field,
            },
        })

        self.f = Formatter()

    def test_to_string(self):
        to_string = self.f.to_string
        values = self.values['title']
        # test a string
        string = to_string(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertEqual(string, 'CEO')

        values = self.values['salary']
        str_num = to_string(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertEqual(str_num, '100000')

        values = self.values['boss']
        bool_num = to_string(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertEqual(bool_num, 'True')

    def test_to_number(self):
        to_num = self.f.to_number
        values = self.values['salary']
        num = to_num(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertEqual(num, 100000)

        values = self.values['boss']
        bool_num = to_num(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertEqual(bool_num, 1)

        values = self.values['title']
        self.assertRaises(Exception, to_num, values['value'], name=values['name'],
                field=values['field'], concept=self.c)

    def test_to_boolean(self):
        to_bool = self.f.to_boolean
        values = self.values['boss']
        bool_str = to_bool(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertEqual(bool_str, True)

        values = self.values['title']
        self.assertRaises(Exception, to_bool, values['value'], name=values['name'],
            field=values['field'], concept=self.c)

        values = self.values['salary']
        self.assertRaises(Exception, to_bool, values['value'], name=values['name'],
            field=values['field'], concept=self.c)

    def test_to_coded(self):
        to_coded = self.f.to_coded
        values = self.values['boss']
        bool_convert = to_coded(values['value'], name=values['name'],
            field=values['field'], concept=self.c)
        self.assertTrue(bool_convert, 1)

        values = self.values['title']
        self.assertRaises(Exception, to_coded, values['value'], name=values['name'],
            field=values['field'], concept=self.c)

    def test_to_html(self):
        class HtmlFormatter(Formatter):
            def to_html(self, values, concept, **context):
                fvalues = self(values, concept, preferred_formats=['string'])
                return OrderedDict({
                    'name': 'Profile',
                    'value': '<span>' + '</span><span>'.join(d['value'] for d in fvalues.values()) + '</span>'
                })
            to_html.process_multiple = True

        f = HtmlFormatter()

        self.assertEqual(OrderedDict({
            'name': 'Profile',
            'value': u'<span>100000</span><span>True</span><span>CEO</span>'
        }), f(self.values, self.c, preferred_formats=['html']))
from avocado.tests.base import BaseTestCase
from avocado.formatters import Formatter
from avocado.models import Field, Concept, ConceptField

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

__all__ = ('FormatterTestCase',)

class FormatterTestCase(BaseTestCase):
    def setUp(self):
        name_field = Field.objects.get_by_natural_key('tests',
            'title', 'name')
        salary_field = Field.objects.get_by_natural_key('tests',
            'title', 'salary')
        boss_field = Field.objects.get_by_natural_key('tests',
            'title', 'boss')

        concept = Concept(name='Title')
        concept.save()

        cf1 = ConceptField(concept=concept, field=name_field, order=1)
        cf1.save()
        cf2 = ConceptField(concept=concept, field=salary_field, order=2)
        cf2.save()
        cf3 = ConceptField(concept=concept, field=boss_field, order=3)
        cf3.save()

        self.values = OrderedDict({
            'name': 'CEO',
            'salary': 100000,
            'boss': True,
        })

        self.cfields = [cf1, cf2, cf3]
        self.f = Formatter(self.cfields)

    def test_to_string(self):
        fvalues = self.f(self.values, preferred_formats=['string'])
        self.assertEqual(OrderedDict({
            'name': 'CEO',
            'salary': '100000',
            'boss': 'True',
        }), fvalues)

    def test_to_number(self):
        fvalues = self.f(self.values, preferred_formats=['number'])
        self.assertEqual(OrderedDict({
            'name': 'CEO',
            'salary': 100000,
            'boss': True,
        }), fvalues)

    def test_to_boolean(self):
        fvalues = self.f(self.values, preferred_formats=['boolean'])
        self.assertEqual(OrderedDict({
            'name': 'CEO',
            'salary': 100000,
            'boss': 1,
        }), fvalues)

    def test_to_coded(self):
        fvalues = self.f(self.values, preferred_formats=['coded'])
        self.assertEqual(OrderedDict({
            'name': 'CEO',
            'salary': 100000,
            'boss': 1,
        }), fvalues)

    def test_to_html(self):
        class HtmlFormatter(Formatter):
            def to_html(self, values, cfields, **context):
                fvalues = self(values, preferred_formats=['string'])
                return OrderedDict({
                    'profile': '<span>' + '</span><span>'.join(fvalues.values()) + '</span>'
                })
            to_html.process_multiple = True

        f = HtmlFormatter(self.cfields)
        fvalues = f(self.values, preferred_formats=['html'])
        self.assertEqual(OrderedDict({
            'profile': u'<span>100000</span><span>CEO</span><span>True</span>'
        }), fvalues)

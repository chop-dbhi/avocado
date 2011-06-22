from django.test import TestCase
from django.core.management import call_command
from avocado.meta.models import Definition

__all__ = ('DefinitionTestCase', 'ConceptTestCase', 'DomainTestCase')

class DefinitionTestCase(TestCase):

    def setUp(self):
        call_command('avocado', 'sync', 'tests', verbosity=0)

    def test_boolean(self):
        d = Definition.objects.get_by_natural_key('tests', 'employee', 'is_manager')

        self.assertTrue(d.model)
        self.assertTrue(d.field)
        self.assertEqual(d.datatype, 'boolean')
        self.assertEqual(d.operators, ('exact', '-exact', 'isnull', '-isnull'))
        self.assertTrue(d.has_choices)

        trans = d.translate(value=False)
        self.assertEqual(str(trans['condition']), "(AND: ('is_manager__exact', False), ('id__isnull', False))")

    def test_integer(self):
        d = Definition.objects.get_by_natural_key('tests', 'title', 'salary')

        self.assertTrue(d.model)
        self.assertTrue(d.field)
        self.assertEqual(d.datatype, 'number')
        self.assertEqual(d.operators, ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range', 'isnull', '-isnull'))
        self.assertFalse(d.has_choices)

        trans = d.translate(value=50000)
        self.assertEqual(str(trans['condition']), "(AND: ('title__salary__exact', 50000.0), ('title__id__isnull', False))")

    def test_string(self):
        d = Definition.objects.get_by_natural_key('tests', 'employee', 'first_name')

        self.assertTrue(d.model)
        self.assertTrue(d.field)
        self.assertEqual(d.datatype, 'string')
        self.assertEqual(d.operators, ('exact', '-exact', 'iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'))
        self.assertFalse(d.has_choices)

        trans = d.translate(value='Robert')
        self.assertEqual(str(trans['condition']), "(AND: ('first_name__exact', u'Robert'), ('id__isnull', False))")


class ConceptTestCase(TestCase):
    pass


class DomainTestCase(TestCase):
    pass

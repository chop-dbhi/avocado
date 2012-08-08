from django.test import TestCase
from django.core import management
from avocado.models import DataField
from ..models import Employee


class TranslatorTestCase(TestCase):
    fixtures = ['query.json']

    def setUp(self):
        management.call_command('avocado', 'sync', 'query', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('query', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('query', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key('query', 'employee', 'first_name')

    def test(self):
        trans = self.is_manager.translate(value=False, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('is_manager__exact', False))")

        trans = self.salary.translate(value=50000, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__exact', 50000.0), ('title__id__isnull', False))")

        trans = self.first_name.translate(value='Robert', tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('first_name__exact', u'Robert'))")

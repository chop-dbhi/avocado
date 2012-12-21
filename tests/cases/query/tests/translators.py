from django.test import TestCase
from django.core import management
from django.core.exceptions import ValidationError
from avocado.models import DataField
from ..models import Employee


class TranslatorTestCase(TestCase):
    fixtures = ['query.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'query', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('query', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('query', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key('query', 'employee', 'first_name')

    def test(self):
        trans = self.is_manager.translate(value=False, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('is_manager__exact', False))")

        trans = self.salary.translate(value=50000, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__exact', 50000.0))")

        trans = self.first_name.translate(value='Robert', tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('first_name__exact', u'Robert'))")

        trans = self.first_name.translate(value=['Robert', None], operator='in',
            tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(OR: ('first_name__in', [u'Robert']), ('first_name__isnull', True))")

        trans = self.salary.translate(value=None, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__isnull', True), ('title__id__isnull', False))")


    def test_dict(self):
        trans = self.is_manager.translate(value={'value': False, 'label': 'No'}, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('is_manager__exact', False))")

        trans = self.salary.translate(value={'value': 50000, 'label': 50000}, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__exact', 50000.0))")

        trans = self.first_name.translate(value={'value': 'Robert', 'label': 'Robert'}, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('first_name__exact', u'Robert'))")

        trans = self.salary.translate(value={'value': None, 'label': 'null'}, tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__isnull', True), ('title__id__isnull', False))")

    def test_non_bool_isnull(self):
        trans = self.is_manager.translate(value=False, operator='isnull', tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('is_manager__isnull', False))")

        trans = self.salary.translate(value=False, operator='isnull', tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__isnull', False), ('title__id__isnull', False))")

        self.assertRaises(ValidationError, self.first_name.translate, value=False, operator='isnull', tree=Employee)

        trans = self.salary.translate(value=False, operator='isnull', tree=Employee)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__isnull', False), ('title__id__isnull', False))")


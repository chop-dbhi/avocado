from django.test import TestCase
from django.core import management
from django.core.exceptions import ValidationError
from avocado.models import DataField
from ....models import Employee, Project


class BaseTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'first_name')
        self.budget = DataField.objects.get_by_natural_key(
            'tests', 'project', 'budget')


class TranslatorTestCase(BaseTestCase):
    def test_bool(self):
        trans = self.is_manager.translate(value=False, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('is_manager__exact', False))")

    def test_bool_isnull(self):
        trans = self.is_manager.translate(
            value=False, operator='isnull', tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('is_manager__isnull', False))")

    def test_int(self):
        trans = self.salary.translate(value=50000, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('title__salary__exact', 50000.0))")

    def test_float_as_int(self):
        trans = self.salary.translate(value=50000.00, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('title__salary__exact', 50000.0))")

    def test_int_null(self):
        trans = self.salary.translate(value=None, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('title__salary__isnull', True), "
                         "('title__id__isnull', False))")

    def test_int_isnull(self):
        trans = self.salary.translate(
            value=False, operator='isnull', tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('title__salary__isnull', False), "
                         "('title__id__isnull', False))")

    def test_char(self):
        trans = self.first_name.translate(value='Robert', tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('first_name__exact', u'Robert'))")

    def test_char_in(self):
        trans = self.first_name.translate(
            value=['Robert', None], operator='in', tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(OR: ('first_name__in', [u'Robert']), "
                         "('first_name__isnull', True))")

    def test_char_isnull(self):
        self.assertRaises(ValidationError, self.first_name.translate,
                          value=False, operator='isnull', tree=Employee)

    def test_decimal(self):
        trans = self.budget.translate(value=50, tree=Project)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('budget__exact', Decimal('50')))")

    def test_decimal_long(self):
        self.assertRaises(ValidationError, self.budget.translate,
                          value=50.3932, tree=Project)


class TranslatorValueDictTestCase(BaseTestCase):
    def test_bool(self):
        trans = self.is_manager.translate(
            value={'value': False, 'label': 'No'}, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('is_manager__exact', False))")

    def test_int(self):
        trans = self.salary.translate(
            value={'value': 50000, 'label': '50000'}, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('title__salary__exact', 50000.0))")

    def test_int_null(self):
        trans = self.salary.translate(
            value={'value': None, 'label': 'null'}, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('title__salary__isnull', True), "
                         "('title__id__isnull', False))")

    def test_char(self):
        trans = self.first_name.translate(
            value={'value': 'Robert', 'label': 'Robert'}, tree=Employee)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('first_name__exact', u'Robert'))")

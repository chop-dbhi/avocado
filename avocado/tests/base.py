from django.test import TestCase
from django.core import management
from avocado.models import DataField

__all__ = ('BaseTestCase',)


class BaseTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        management.call_command('avocado', 'sync', 'tests')
        self.is_manager = DataField.objects.get_by_natural_key('tests', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('tests', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key('tests', 'employee', 'first_name')

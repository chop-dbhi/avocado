from django.test import TestCase
from django.core.management import call_command
from avocado.meta.models import Definition

__all__ = ('BaseTestCase',)

class BaseTestCase(TestCase):

    def setUp(self):
        call_command('avocado', 'sync', 'tests', verbosity=0)
        self.is_manager = Definition.objects.get_by_natural_key('tests', 'employee', 'is_manager')
        self.salary = Definition.objects.get_by_natural_key('tests', 'title', 'salary')
        self.first_name = Definition.objects.get_by_natural_key('tests', 'employee', 'first_name')

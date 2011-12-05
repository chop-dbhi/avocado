from django.test import TestCase
from django.core.management import call_command
from avocado.meta.models import Field

__all__ = ('BaseTestCase',)

class BaseTestCase(TestCase):
    fixtures = ['test_meta.json', 'test_data.json']

    def setUp(self):
        self.is_manager = Field.objects.get_by_natural_key('tests', 'employee', 'is_manager')
        self.salary = Field.objects.get_by_natural_key('tests', 'title', 'salary')
        self.first_name = Field.objects.get_by_natural_key('tests', 'employee', 'first_name')

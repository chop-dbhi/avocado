import os
import sys
from django.test import TestCase
from django.core import management
from avocado.models import DataField, DataConcept, DataContext, DataView

__all__ = ('CommandsTestCase',)

class CommandsTestCase(TestCase):
    fixtures = ['employee_data.json', 'legacy.json']

    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout = self.stdout

    def test_subcommands(self):
        management.call_command('avocado', 'init', 'tests')
        management.call_command('avocado', 'cache', 'tests')
        management.call_command('avocado', 'check', output='none')
        management.call_command('avocado', 'history', cull=True)

        # Before updating the data, the data_version be at the default value 1
        self.assertEqual(DataField.objects.filter()[:1].get().data_version, 1)

        management.call_command('avocado', 'data', 'tests', incr_version=True)

        # After calling the data command with the incr_version argument
        # set to True, we should see an incremented data_version of 2
        self.assertEqual(DataField.objects.filter()[:1].get().data_version, 2)

        management.call_command('avocado', 'data', 'tests')

        # Confirm that calling the data command without the optional
        # incr_version argument does not cause the data_version field
        # to get incremented.
        self.assertEqual(DataField.objects.filter()[:1].get().data_version, 2)

    def test_init(self):
        management.call_command('avocado', 'init', 'tests')
        self.assertEqual(DataField.objects.filter(published=True).count(), 18)
        self.assertEqual(DataConcept.objects.filter(published=True).count(), 18)

    def test_init_previous(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                concepts=False)
        self.assertEqual(DataField.objects.filter(published=False).count(), 18)
        self.assertEqual(DataConcept.objects.filter().count(), 0)

    def test_legacy(self):
        from avocado.models import DataField
        management.call_command('avocado', 'legacy', no_input=True)
        fields = DataField.objects.all()

        # 2/3 have been migrated
        self.assertEqual(len(fields), 2)

        f1 = DataField.objects.get_by_natural_key('tests', 'title', 'name')
        # Turned on the enumerable flag
        self.assertTrue(f1.enumerable)
        self.assertFalse(f1.published)

        f1 = DataField.objects.get_by_natural_key('tests', 'title', 'salary')
        # Turned off the enumerable flag
        self.assertFalse(f1.enumerable)
        self.assertFalse(f1.enumerable)

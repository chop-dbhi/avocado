import os
import sys
from django.test import TestCase
from django.core import management
from avocado.models import DataField, DataContext, DataView

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
        management.call_command('avocado', 'check')
        
        # Before updating the data, the data_version be at the default value 1
        self.assertEqual(DataField.objects.filter()[:1].get().data_version, 1)

        management.call_command('avocado', 'data', 'tests', update_data_version=True)
        
        # After calling the data command with the update_data_version argument
        # set to True, we should see an incremented data_version of 2
        self.assertEqual(DataField.objects.filter()[:1].get().data_version, 2)
        
        management.call_command('avocado', 'data', 'tests')
        
        # Confirm that calling the data command without the optional 
        # update_data_version argument does not cause the data_version field
        # to get incremented.
        self.assertEqual(DataField.objects.filter()[:1].get().data_version, 2)

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

    def test_history(self):
        for _ in xrange(200):
            DataContext(archived=True).save()
            DataView(archived=True).save()

        oldest_context = DataContext.objects.get(pk=1)
        latest_context = DataContext.objects.get(pk=200)

        # Nothing should happen
        management.call_command('avocado', 'history')

        self.assertEqual(DataContext.objects.count(), 200)
        self.assertEqual(DataView.objects.count(), 200)

        management.call_command('avocado', 'history', prune=True)

        self.assertEqual(DataContext.objects.count(), 50)
        self.assertEqual(DataView.objects.count(), 50)

        # Just to ensure the ordering is correct.. e.g. the newer ones stay
        # around
        self.assertTrue(DataContext.objects.filter(pk=latest_context.pk).exists())
        self.assertFalse(DataContext.objects.filter(pk=oldest_context.pk).exists())

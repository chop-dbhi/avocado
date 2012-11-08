import os
import sys
from django.test import TestCase
from django.core import management


class CommandsTestCase(TestCase):
    fixtures = ['subcommands_legacy.json']

    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout = self.stdout

    def test_subcommands(self):
        management.call_command('avocado', 'sync', 'subcommands')
        management.call_command('avocado', 'cache', 'subcommands')
        management.call_command('avocado', 'orphaned')
        management.call_command('avocado', 'data', 'subcommands', update_data_modified=True)

    def test_legacy(self):
        from avocado.models import DataField
        management.call_command('avocado', 'legacy', no_input=True)
        fields = DataField.objects.all()

        # 2/3 have been migrated
        self.assertEqual(len(fields), 2)

        f1 = DataField.objects.get_by_natural_key('subcommands', 'title', 'name')
        # Turned on the enumerable flag
        self.assertTrue(f1.enumerable)
        self.assertFalse(f1.published)

        f1 = DataField.objects.get_by_natural_key('subcommands', 'title', 'salary')
        # Turned off the enumerable flag
        self.assertFalse(f1.enumerable)
        self.assertFalse(f1.enumerable)

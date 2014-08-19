import django
import os
import sys
from django.test import TestCase
from django.core import management
from django.core.management.base import CommandError
from avocado.models import DataField, DataConcept, DataCategory

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
        management.call_command('avocado', 'cache', 'tests', flush=True)

        # Old versions of Django trap the CommandError and call sys.exit(1)
        # instead of re-raising the CommandError for it to be handled at a
        # higher level.
        if django.VERSION < (1, 5):
            self.assertRaises(SystemExit, management.call_command, 'avocado',
                              'cache', 'tests', methods=['invalid_function'])
        else:
            self.assertRaises(CommandError, management.call_command, 'avocado',
                              'cache', 'tests', methods=['invalid_function'])

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

        fields = DataField.objects.filter(published=True)
        concepts = DataConcept.objects.filter(published=True)

        self.assertEqual(fields.count(), 18)
        self.assertEqual(concepts.count(), 18)

    def test_init_categories(self):
        management.call_command('avocado', 'init', 'tests.employee',
                                categories=True)

        self.assertTrue(DataCategory.objects.filter(name='Employee',
                                                    published=True).exists())

    def test_init_previous(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False)

        fields = DataField.objects.filter(published=False)
        self.assertEqual(fields.count(), 18)
        self.assertEqual(DataConcept.objects.count(), 0)

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

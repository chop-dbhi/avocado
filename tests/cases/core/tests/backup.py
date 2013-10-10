import os
from django.core import management
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings

TEST_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@override_settings(SOUTH_TESTS_MIGRATE=True)
class BackupTestCase(TransactionTestCase):
    def test_fixture_dir(self):
        from avocado.core import backup
        self.assertEqual(backup.get_fixture_dir(), os.path.join(TEST_APP_DIR, 'fixtures'))

    def test_safe_load_tmp(self):
        from avocado.core import backup
        from avocado.models import DataField

        management.call_command('avocado', 'init', 'tests')
        self.assertEqual(DataField.objects.count(), 18)

        backup_path = backup.safe_load('0001_avocado_metadata')

        self.assertTrue(os.path.exists(backup_path))
        self.assertEqual(DataField.objects.count(), 3)
        os.remove(backup_path)

    def test_safe_load(self):
        from avocado.core import backup
        from avocado.models import DataField

        management.call_command('avocado', 'init', 'tests')
        self.assertEqual(DataField.objects.count(), 18)

        backup_path = backup.safe_load('0001_avocado_metadata',
            backup_path='backup.json')

        self.assertTrue(os.path.exists('backup.json'))
        self.assertEqual(DataField.objects.count(), 3)
        os.remove(backup_path)

    def test_fixture_filenames(self):
        from avocado.core import backup
        filenames = backup._fixture_filenames(backup.get_fixture_dir())
        self.assertEqual(filenames, ['0001_avocado_metadata.json'])

    def test_next_fixture_name(self):
        from avocado.core import backup
        from avocado.conf import settings
        filename = backup.next_fixture_name(settings.METADATA_FIXTURE_SUFFIX,
            backup.get_fixture_dir())
        self.assertEqual(filename, '0002_avocado_metadata')

    def test_migration_call(self):
        from avocado.core import backup
        management.call_command('avocado', 'migration')
        migration_dir = os.path.join(TEST_APP_DIR, 'migrations')
        self.assertTrue(os.path.exists(os.path.join(migration_dir, '0002_avocado_metadata_migration.py')))
        os.remove(os.path.join(migration_dir, '0002_avocado_metadata_migration.py'))
        os.remove(os.path.join(backup.get_fixture_dir(), '0002_avocado_metadata.json'))

    def test_migration(self):
        management.call_command('migrate', 'core')

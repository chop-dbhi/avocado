import os
from django.core import management
from django.core.exceptions import ImproperlyConfigured
from django.test import TransactionTestCase
from django.test.utils import override_settings

TEST_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _get_migrations():
    from south.models import MigrationHistory
    return list(MigrationHistory.objects.all()
                .order_by('id')
                .values_list('migration', flat=True))


@override_settings(SOUTH_TESTS_MIGRATE=True)
class BackupTestCase(TransactionTestCase):
    def test_fixture_dir(self):
        from avocado.core import backup
        self.assertEqual(backup.get_fixture_dir(),
                         os.path.join(TEST_APP_DIR, 'fixtures'))

    def test_safe_load_tmp(self):
        from avocado.core import backup
        from avocado.models import DataField

        management.call_command('avocado', 'init', 'tests', quiet=True)
        self.assertEqual(DataField.objects.count(), 18)

        backup_path = backup.safe_load('0001_avocado_metadata')

        self.assertTrue(os.path.exists(backup_path))
        self.assertEqual(DataField.objects.count(), 3)
        os.remove(backup_path)

    def test_safe_load(self):
        from avocado.core import backup
        from avocado.models import DataField

        management.call_command('avocado', 'init', 'tests', quiet=True)
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
        from south import migration
        management.call_command('avocado', 'migration', quiet=True)
        migration_dir = os.path.join(TEST_APP_DIR, 'migrations')
        self.assertTrue(os.path.exists(os.path.join(migration_dir,
                                       '0002_avocado_metadata_migration.py')))
        os.remove(os.path.join(migration_dir,
                               '0002_avocado_metadata_migration.py'))
        os.remove(os.path.join(backup.get_fixture_dir(),
                               '0002_avocado_metadata.json'))
        # TransactionTestCase rolls back the database after each test case,
        # but South does not know this, courtesy of caching in
        # migration.Migrations.
        migration.Migrations._clear_cache()

    def test_migration_call_no_fake(self):
        # This test superficially looks like it tests the --no-fake switch,
        # but it doesn't fully succeed, because the Django managemement
        # API can't duplicate the behavior of command line boolean switches.
        # The --no-fake switch bug (#171) can't be tested via the internal
        # API.  In fact, any test case for a boolean switch has to
        # execute a shell command.  That opens a can of worms, because
        # to perform a migration in a shell command, we would have to replace
        # TransactionTestCase with TestCase, which would require substantial
        # changes to this test class.  This is an awful lot of work for one
        # trivial bug fix.
        from avocado.core import backup
        from south import migration
        management.call_command('avocado', 'migration', no_fake=True,
                                quiet=True)
        migrations = _get_migrations()
        self.assertEqual(migrations, [])
        migration_dir = os.path.join(TEST_APP_DIR, 'migrations')
        self.assertTrue(os.path.exists(os.path.join(migration_dir,
                                       '0002_avocado_metadata_migration.py')))
        os.remove(os.path.join(migration_dir,
                               '0002_avocado_metadata_migration.py'))
        os.remove(os.path.join(backup.get_fixture_dir(),
                               '0002_avocado_metadata.json'))
        migration.Migrations._clear_cache()

    def test_migration(self):
        management.call_command('migrate', 'core', verbosity=0)

    def test_missing_setting(self):
        from avocado.conf import settings
        previous = settings.METADATA_MIGRATION_APP
        setattr(settings._wrapped, 'METADATA_MIGRATION_APP', None)
        try:
            from avocado.core import backup  # noqa
            backup._check_app()
            self.assertTrue(False)
        except ImproperlyConfigured:
            self.assertTrue(True)
        finally:
            setattr(settings._wrapped, 'METADATA_MIGRATION_APP', previous)

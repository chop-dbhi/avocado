from south.migration import Migrations
from django.core.management import call_command
from django.test import TransactionTestCase
from avocado.models import DataConcept, DataConceptField, DataField


class MigrationTestCase(TransactionTestCase):
    start_migration = None
    dest_migration = None
    django_application = 'avocado'

    def setUp(self):
        super(MigrationTestCase, self).setUp()
        migrations = Migrations(self.django_application)
        self.start_orm = migrations[self.start_migration].orm()
        self.dest_orm = migrations[self.dest_migration].orm()

        # Ensure the migration history is up-to-date with a fake migration.
        # The other option would be to use the south setting for these tests
        # so that the migrations are used to setup the test db.
        call_command('migrate', self.django_application, fake=True,
                     verbosity=0)
        # Then migrate back to the start migration.
        call_command('migrate', self.django_application, self.start_migration,
                     verbosity=0)

    def tearDown(self):
        # Leave the db in the final state so that the test runner doesn't
        # error when truncating the database.
        call_command('migrate', self.django_application, verbosity=0)

    def migrate_to_dest(self):
        call_command('migrate', self.django_application, self.dest_migration,
                     verbosity=0)


class Migration0035TestCase(MigrationTestCase):
    start_migration = '0034_auto__add_field_datafield_type'
    dest_migration = '0035_fix_concept_field_order'

    def test(self):
        c = DataConcept(name='Creds')
        c.save()

        for field_name in ('first_name', 'last_name', 'title', 'is_manager'):
            f = DataField(app_name='tests', model_name='employee',
                          field_name=field_name)
            f.save()

            # Saved with default ordering or 0
            DataConceptField(concept=c, field=f).save()

        self.migrate_to_dest()

        # Fetch fields
        cfields = DataConceptField.objects.filter(concept=c)
        self.assertEqual(list(cfields.values_list('order', flat=True)),
                         range(4))

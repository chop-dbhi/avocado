import re
import os
import logging
from optparse import make_option
from django.db import DEFAULT_DB_ALIAS
from django.core.exceptions import ImproperlyConfigured
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from south import migration
from south.creator import freezer
from avocado.conf import settings
from avocado.core import backup

METADATA_FIXTURE_SUFFIX = settings.METADATA_FIXTURE_SUFFIX
METADATA_MIGRATION_SUFFIX = settings.METADATA_MIGRATION_SUFFIX

METADATA_MIGRATION_TEMPLATE = u"""\
# -*- coding: utf-8 -*-
from south.v2 import DataMigration

class Migration(DataMigration):

    depends_on = (
       ("avocado", "{latest_avocado_migration}"),
    )

    def forwards(self, orm):
        "Perform a 'safe' load using Avocado's backup utilities."
        from avocado.core import backup
        backup.safe_load({fixture_name}, backup_path={backup_path},
            using={using})

    def backwards(self, orm):
        "No backwards migration applicable."
        pass

    models = {frozen_models}
"""

log = logging.getLogger(__name__)


_help = """\
Simple utility for dumping Avocado metadata.

The migation command requires that the METADATA_MIGRATION_APP setting be
defined in the AVOCADO dict:

AVOCADO = {
    'METADATA_MIGRATION_APP': 'someapp',
    ...
}

See https://github.com/cbmi/avocado/wiki/Managing-your-metadata.\
"""


class Command(BaseCommand):
    __doc__ = help = _help

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS, help='Nominates a specific '
                    'database to dump fixtures from. Defaults to the '
                    '"default" database.'),
        make_option('--backup-path', action='store', dest='backup_path',
                    help='Define a non-temporary path for the migration '
                    'backup.'),
        make_option('--no-fake', action='store_true', help='Prevents the new '
                    'migration from being immediately faked in the database.')
    )

    def handle(self, migration_suffix=METADATA_MIGRATION_SUFFIX,
               fixture_suffix=METADATA_FIXTURE_SUFFIX, **options):
        database = options.get('database')
        verbosity = options.get('verbosity')
        backup_path = options.get('backup_path')
        no_fake = options.get('no_fake')

        try:
            fixture_dir = backup.get_fixture_dir()
        except ImproperlyConfigured, e:
            raise CommandError(e.message)

        if not os.path.exists(fixture_dir):
            os.makedirs(fixture_dir)
            log.info(u'Created fixture directory: {0}'.format(fixture_dir))
        elif not os.path.isdir(fixture_dir):
            raise CommandError(u'The metadata fixture directory {0}.. is not '
                               'a directory.'.format(fixture_dir))

        # Only allow valid names
        if re.search('[^_\w]', migration_suffix):
            raise CommandError('Migration names should contain only '
                               'alphanumeric characters and underscores.')

        fixture_name = backup.next_fixture_name(fixture_suffix, fixture_dir)
        backup.create_fixture(fixture_name, using=database)

        if verbosity > 1:
            log.info(u'Created fixture {0}'.format(fixture_name))

        # Get the last migration for avocado to insert it as a dependency
        avocado_migrations = migration.Migrations('avocado',
                                                  force_creation=False)
        avocado_migration_name = avocado_migrations[-1].name()

        # Get the Migrations for this app(creating the migration dir if needed)
        migrations = migration.Migrations(settings.METADATA_MIGRATION_APP,
                                          force_creation=True,
                                          verbose_creation=verbosity > 0)

        # See what filename is next in line. We assume they use numbers.
        next_filename = migrations.next_filename(migration_suffix)

        # Normally, South would freeze the Avocado models(since we are
        # dependent on them) along with this app's models and store the frozen
        # representation in the migration. Since we are building the
        # migration ourselves, we need to freeze and write the models to the
        # migration.
        frozen_models = freezer.freeze_apps_to_string([
            'avocado', settings.METADATA_MIGRATION_APP])

        file_contents = METADATA_MIGRATION_TEMPLATE.format(
            latest_avocado_migration=avocado_migration_name,
            fixture_name=repr(fixture_name),
            backup_path=(backup_path and repr(backup_path) or backup_path),
            using=repr(database),
            frozen_models=frozen_models)

        file_path = os.path.join(migrations.migrations_dir(), next_filename)

        with open(file_path, 'w') as fout:
            fout.write(file_contents)

        log.info(u'Created migration {0}'.format(next_filename))

        if not no_fake:
            # Clear and reload migrations..
            [migrations.pop() for _ in xrange(len(migrations))]
            migrations._load_migrations_module(
                migrations.application.migrations)

            # Fake migrations up to the current created one..
            management.call_command('migrate', settings.METADATA_MIGRATION_APP,
                                    os.path.splitext(next_filename)[0],
                                    fake=True, database=database, verbosity=0)

            log.info('Faked migrations up to the current one')

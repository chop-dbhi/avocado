from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import transaction
from avocado.core import utils
from avocado.models import DataField
from avocado.legacy import models as legacy


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado legacy [options]

    DESCRIPTION:

        Utilities for migrating Avocado 1.x metadata to the
        Avocado 2.x data model.

    OPTIONS:

        ``--force`` - Forces legacy description data to override existing
            fields.

        ``--no-input`` - Prevent user prompts and assumes the default behavior
            during migration.
    """

    help = '\n'.join([
        'Utilities for migrating Avocado 1.x metadata to the',
        'Avocado 2.x data model.',
    ])

    option_list = BaseCommand.option_list + (
        make_option('-f', '--force', action='store_true',
            dest='force', default=False,
            help='During a migration, force and update on existing fields'),

        make_option('--no-input', action='store_true',
            dest='no_input', default=False,
            help='Prevents user prompts and performs the default bahavior'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        force = options.get('force')
        no_input = options.get('no_input')

        total_migrated = 0

        for lf in legacy.Field.objects.iterator():
            try:
                f = DataField.objects.get_by_natural_key(lf.app_name,
                    lf.model_name, lf.field_name)
            except DataField.DoesNotExist:
                f = DataField(app_name=lf.app_name, model_name=lf.model_name,
                    field_name=lf.field_name)

            qualified_name = '({0}) {1}.{2}'.format(f.app_name, f.model_name,
                f.field_name)

            if f.pk and not force:
                print '{0} already exists. Skipping...'.format(qualified_name)
                continue

            # Check if this is an orphan
            if not f.field:
                print '{0} is orphaned. Skipping...'.format(qualified_name)
                continue

            # Map various fields
            f.name = lf.name
            f.description = lf.description
            f.keywords = lf.keywords
            f.translator = lf.translator
            f.group_id = lf.group_id

            print 'Migrating...\t{0}'.format(qualified_name)

            flags = utils.get_heuristic_flags(f)
            f.__dict__.update(flags)

            # Disagreement with enumerable status
            if not no_input and f.enumerable != lf.enable_choices:
                if lf.enable_choices:
                    override = raw_input('"{0}" is marked as enumerable, but '
                        'does not qualify to be enumerable. Override? '
                        '[y/N] '.format(qualified_name))
                else:
                    override = raw_input('"{0}" is not marked as enumerable, '
                        'but qualifies to be enumerable. Override? '
                        '[y/N] '.format(qualified_name))

                if override.lower() == 'y':
                    f.enumerable = lf.enable_choices

            f.save()
            f.sites = lf.sites.all()

            total_migrated += 1

        print 'Fields migrated:\t{0}'.format(total_migrated)

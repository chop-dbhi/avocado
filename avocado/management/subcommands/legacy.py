from optparse import make_option
from django.core.management.base import BaseCommand
from avocado.core import utils
from avocado.models import DataField, DataConcept, DataCategory
from avocado.legacy import models as legacy


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado legacy [options]

    DESCRIPTION:

        Utilities for migrating Avocado 1.x metadata to the
        Avocado 2.x data model.

    OPTIONS:

        ``--include-non-editable`` - Create ``DataField`` instances for fields marked
        as not editable (i.e. ``editable=False``).
    """

    help = '\n'.join([
        'Utilities for migrating Avocado 1.x metadata to the',
        'Avocado 2.x data model.',
    ])

    option_list = BaseCommand.option_list + (
        make_option('-m', '--migrate', action='store_true',
            dest='migrate', default=False,
            help='Performs the migration'),

        make_option('-e', '--exclude-orphans', action='store_true',
            dest='exclude_orphans', default=False,
            help='During a migration, exclude orphaned fields'),

        make_option('-u', '--update', action='store_true',
            dest='update_existing', default=False,
            help='During a migration, update existing fields'),
    )


    def handle(self, *args, **options):
        migrate = options.get('migrate', False)
        exclude_orphans = options.get('exclude_orphans', False)
        update_existing = options.get('update_existing', False)

        field_cache = {}
        total_migrated = 0

        for lfield in legacy.Field.objects.iterator():
            already_exists = False

            try:
                f = DataField.objects.get_by_natural_key(lfield.app_name,
                    lfield.model_name, lfield.field_name)
                already_exists = True
            except DataField.DoesNotExist:
                f = DataField(app_name=lfield.app_name, model_name=lfield.model_name,
                    field_name=lfield.field_name)

            if already_exists and not update_existing:
                print '({}) {}.{} already exists. Skipping...'.format(f.app_name, f.model_name, f.name)
                continue

            # Map various fields
            f.name = lfield.name,
            f.description = lfield.description
            f.keywords = lfield.keywords
            f.published = lfield.is_public
            f.translator = lfield.translator
            f.group_id = lfield.group_id

            # Check if this is an orphan
            if exclude_orphans and not f.field:
                print '({}) {}.{} is orphaned. Skipping...'.format(f.app_name, f.model_name, f.name)
                continue

            print 'Migrating...\t({}) {}.{}'.format(f.app_name, f.model_name, f.name)

            flags = utils.get_heuristic_flags(f)
            f.__dict__.update(flags)

            # Disagreement with enumerable status
            if f.enumerable != lfield.enable_choices:
                if lfield.enable_choices:
                    override = raw_input('"{}" is marked as enumerable, but does not qualify to be enumerable. Override? [y/n] ')
                else:
                    override = raw_input('"{}" is not marked as enumerable, but qualifies to be enumerable. Override? [y/n] ')

                if override.lower() == 'y':
                    f.enumerable = lfield.enable_choices

            if migrate:
                f.save()
                # Cache for Concept processing
                field_cache[f.pk] = f

                # Now that it is saved, associate related objects
                f.sites = lfield.sites.all()
            total_migrated += 1

        print 'Fields migrated:\t{:,}'.format(total_migrated)

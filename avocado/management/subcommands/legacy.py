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

        make_option('-n', '--no-input', action='store_true',
            dest='no_input', default=False,
            help='During a migration, do not prompt for user input, ' \
                    'e.g. assume the defaults.'),
    )

    def handle(self, *args, **options):
        migrate = options.get('migrate')
        exclude_orphans = options.get('exclude_orphans')
        update_existing = options.get('update_existing')
        no_input = options.get('no_input')

        field_cache = {}
        total_migrated = 0

        current_label = None

        for lfield in legacy.Field.objects.order_by('app_name', 'model_name').iterator():
            orphan = False
            already_exists = False

            label = '{}.{}'.format(lfield.app_name, lfield.model_name)
            if current_label != label:
                current_label = label
                print '\n{}'.format(current_label)
                print '-' * 5

            try:
                f = DataField.objects.get_by_natural_key(lfield.app_name,
                    lfield.model_name, lfield.field_name)
                already_exists = True
            except DataField.DoesNotExist:
                f = DataField(app_name=lfield.app_name, model_name=lfield.model_name,
                    field_name=lfield.field_name)

            if already_exists and not update_existing:
                print u'{} already exists. Skipping...'.format(f)
                continue

            if f.model is None:
                orphan = True
                if exclude_orphans:
                    print u'Model "{}" does not exist. Skipping...'.format(f.model)
                    continue

            if f.field is None:
                orphan = True
                if exclude_orphans:
                    print u'Model field "{}.{}" does not exist. Skipping...'.format(f.model_name, f.field_name)
                    continue

            # Map various fields
            f.name = lfield.name
            f.description = lfield.description
            f.keywords = lfield.keywords
            f.published = lfield.is_public
            f.translator = lfield.translator
            f.group_id = lfield.group_id

            print u'Migrating: {} [{}]'.format(f.name, f.field_name)

            if not orphan:
                flags = utils.get_heuristic_flags(f)
                f.__dict__.update(flags)

                # Disagreement with enumerable status
                if f.enumerable != lfield.enable_choices:
                    if no_input:
                        f.enumerable = lfield.enable_choices
                        print u'- Setting "enumerable" to {}'.format(f.enumerable)
                    else:
                        if lfield.enable_choices:
                            override = raw_input('\n{} [{}] is marked as enumerable, but does not qualify to be enumerable. Override? [y/n] '.format(f.name, f.field_name))
                        else:
                            override = raw_input('\n{} [{}] {} is not marked as enumerable, but qualifies to be enumerable. Override? [y/n] '.format(f.name, f.field_name))
                        print

                        if override.lower() == 'y':
                            f.enumerable = lfield.enable_choices
                            print u'- Setting "enumerable" to {}'.format(f.enumerable)

            if migrate:
                f.save()
                # Cache for Concept processing
                field_cache[f.pk] = f

                # Now that it is saved, associate related objects
                f.sites = lfield.sites.all()
            total_migrated += 1

        print '{:,} fields migrated'.format(total_migrated)

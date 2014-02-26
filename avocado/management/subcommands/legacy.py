from optparse import make_option
from django.db import transaction
from django.db.models import Q
from django.core.management.base import BaseCommand
from avocado.core import utils
from avocado.models import DataField, DataCategory, DataConcept, \
    DataConceptField
from avocado.legacy import models as legacy


class Command(BaseCommand):
    help = "Utilities for migrating Avocado 1.x metadata to the Avocado 2.x "
    "data model."

    option_list = BaseCommand.option_list + (
        make_option('-f', '--force', action='store_true', dest='force',
                    default=False, help='During a migration, force an update '
                    'to existing data.'),

        make_option('--no-input', action='store_true', dest='no_input',
                    default=False, help='Prevents user prompts and performs '
                    'the default bahavior'),

        make_option('--no-fields', action='store_false', dest='fields',
                    default=True, help='Do migrate legacy Field instances to '
                    'DataField'),

        make_option('--no-columns', action='store_false', dest='columns',
                    default=True, help='Do migrate legacy Column instances to '
                    'DataConcept'),

        make_option('--no-criteria', action='store_false', dest='criteria',
                    default=True, help='Do migrate legacy Criterion instances '
                    'to DataConcept'),

        make_option('--no-categories', action='store_false', dest='categories',
                    default=True, help='Do migrate legacy Category instances '
                    'to DataCategory'),
    )

    def _migrate_categories(self, **options):
        total_migrated = 0

        # Migrate categories without a parent first
        for lc in legacy.Category.objects.order_by('-parent').iterator():
            kwargs = {
                'name__iexact': lc.name,
            }
            # Filter by parent if one exists since categories with the same
            # name can exists as sub-categories.
            if lc.parent_id:
                kwargs['parent__name'] = lc.parent.name

            if DataCategory.objects.filter(**kwargs).exists():
                print '"{0}" already exists. Skipping...'.format(lc)
                continue

            if lc.parent_id:
                try:
                    p = DataCategory.objects.get(name=lc.parent.name)
                except DataCategory.DoesNotExist:
                    print('Parent category "{0}" does not exist for "{1}". '
                          'Skipping...'.format(lc.parent.name, lc.name))
                    continue
            else:
                p = None

            c = DataCategory(name=lc.name, parent=p, order=lc.order)
            c.save()
            print 'Migrated "{0}"'.format(c)
            total_migrated += 1

        print u'Categories migrated:\t{0}'.format(total_migrated)

    def _migrate_fields(self, **options):
        force = options.get('force')
        no_input = options.get('no_input')

        total_migrated = 0

        for lf in legacy.Field.objects.iterator():
            try:
                f = DataField.objects.get_by_natural_key(lf.app_name,
                                                         lf.model_name,
                                                         lf.field_name)
            except DataField.DoesNotExist:
                f = DataField(app_name=lf.app_name, model_name=lf.model_name,
                              field_name=lf.field_name)

            qualified_name = \
                u'({0}) {1}.{2}'.format(f.app_name, f.model_name, f.field_name)

            if f.pk and not force:
                print u'{0} already exists. Skipping...'.format(qualified_name)
                continue

            # Check if this is an orphan
            if not f.field:
                print u'{0} is orphaned. Skipping...'.format(qualified_name)
                continue

            # Map various fields
            f.name = lf.name
            f.description = lf.description
            f.keywords = lf.keywords
            f.translator = lf.translator
            f.group_id = lf.group_id

            print u'Migrated "{0}"'.format(qualified_name)

            f.__dict__.update(utils.get_heuristic_flags(f.field))

            # Disagreement with enumerable status
            if not no_input and f.enumerable != lf.enable_choices:
                if lf.enable_choices:
                    override = raw_input(u'"{0}" is marked as enumerable, but '
                                         'does not qualify to be enumerable. '
                                         'Override? [y/N] '
                                         .format(qualified_name))
                else:
                    override = raw_input(u'"{0}" is not marked as enumerable, '
                                         'but qualifies to be enumerable. '
                                         'Override? [y/N] '
                                         .format(qualified_name))

                if override.lower() == 'y':
                    f.enumerable = lf.enable_choices

            f.save()
            f.sites = lf.sites.all()

            total_migrated += 1

        print u'Fields migrated:\t{0}'.format(total_migrated)

    def _migrate_concept(self, model, migrate_func, **options):
        no_input = options.get('no_input')

        total_migrated = 0

        for lc in model.objects.iterator():
            field_nks = list(lc.fields.values('app_name', 'model_name',
                                              'field_name').distinct())
            field_cond = Q()

            for f in field_nks:
                field_cond = field_cond | Q(**f)

            fields = DataField.objects.filter(field_cond).distinct()

            # Mismatch of fields from new to old
            if len(fields) != len(field_nks):
                print('One or more fields mismatched for "{0}". '
                      'Skipping...'.format(lc))
                continue

            matches = DataConcept.objects.filter(name=lc.name)

            # Filter concepts by existence of fields
            for f in fields:
                matches = matches.filter(fields__app_name=f.app_name,
                                         fields__model_name=f.model_name,
                                         fields__field_name=f.field_name)

            num = len(matches)

            if num > 1:
                print('{0} have the same name and fields. '
                      'Skipping...'.format(num))
                continue

            if num == 1:
                c = matches[0]
                existing = True

                if not no_input:
                    override = True
                    while True:
                        response = raw_input(u'Match found for "{0}". '
                                             'Override? [n/Y] '.format(c))
                        if not response:
                            break
                        if response.lower() == 'n':
                            override = False
                            break
                    if not override:
                        continue
            else:
                c = DataConcept(queryable=False, viewable=False)
                existing = False

            c.name = lc.name
            c.order = lc.order
            c.published = lc.is_public

            # This looks odd, but this handles choosing the longer of the two
            # descriptions for criterion and column if both exist.
            if not c.description or lc.description and \
                    len(lc.description) > len(c.description):
                c.description = lc.description

            if lc.category:
                try:
                    kwargs = {
                        'name__iexact': lc.category.name,
                    }
                    # Filter by parent if one exists since categories with the
                    # same name can exists as sub-categories.
                    if lc.category.parent_id:
                        kwargs['parent__name'] = lc.category.parent.name
                    c.category = DataCategory.objects.get(**kwargs)
                except DataCategory.DoesNotExist:
                    pass

            # Apply migration specific function to concept from legacy concept
            migrate_func(c, lc)

            # Save for foreign key references to concept fields
            c.save()

            cfs = []

            if not existing:
                lcfs = list(lc.conceptfields.select_related('field'))

                # Dict of legacy concept fields to the new field it
                # corresponds to
                lcf_map = {}

                for lcf in lcfs:
                    for f in fields:
                        # Match and break
                        if lcf.field.natural_key() == f.natural_key():
                            lcf_map[lcf.pk] = f
                            break

                # Map fields to
                # Iterate over all legacy concept fields and create the new
                # concept fields
                for lcf in lcfs:
                    f = lcf_map[lcf.pk]
                    cfs.append(DataConceptField(concept=c, field=f,
                                                name=lcf.name,
                                                order=lcf.order))

            # Save concept fields
            for cf in cfs:
                cf.save()

            print 'Migrated "{0}"'.format(c)
            total_migrated += 1

        print '{0} migrated: {1}'.format(model.__name__, total_migrated)

    def _migrate_criteria(self, **options):
        def func(c, lc):
            c.queryable = True
        self._migrate_concept(legacy.Criterion, func, **options)

    def _migrate_columns(self, **options):
        def func(c, lc):
            c.viewable = True
            c.formatter_name = lc.html_fmtr
        self._migrate_concept(legacy.Column, func, **options)

    def handle(self, **options):
        if options.get('categories'):
            with transaction.commit_on_success():
                self._migrate_categories(**options)
        if options.get('fields'):
            with transaction.commit_on_success():
                self._migrate_fields(**options)
        if options.get('criteria'):
            with transaction.commit_on_success():
                self._migrate_criteria(**options)
        if options.get('columns'):
            with transaction.commit_on_success():
                self._migrate_columns(**options)

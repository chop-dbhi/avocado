import os
import sys
from optparse import make_option
from django.db.models import get_model, get_models, get_app, AutoField, \
    ForeignKey, OneToOneField, ManyToManyField, FieldDoesNotExist
from django.core.management.base import BaseCommand
from avocado.models import DataField, DataConcept, DataCategory
from avocado.core import utils


_help = """\
Finds all models referenced by the app, model or field `labels` and
attempts to create a `DataField` instance per model field.
Any `DataField` already loaded will not be altered in any way.
"""


class Command(BaseCommand):
    __doc__ = help = _help

    option_list = BaseCommand.option_list + (
        make_option('--no-publish', action='store_false', dest='publish',
                    default=True, help='Prevent publishing fields or '
                    'concepts.'),

        make_option('--no-concepts', action='store_false', dest='concepts',
                    default=True, help='Prevent creating concepts.'),

        make_option('-e', '--include-non-editable', action='store_true',
                    dest='include_non_editable', default=False, help='Create '
                    'fields for non-editable fields'),

        make_option('-k', '--include-keys', action='store_true',
                    dest='include_keys', default=False, help='Create fields '
                    'for primary and foreign key fields'),

        make_option('-f', '--force', action='store_true', dest='force',
                    default=False, help='Forces an update on existing field '
                    'metadata'),

        make_option('-q', '--quiet', action='store_true', dest='quiet',
                    default=False, help='Do not print any output'),

        make_option('--prepend-model-name', action='store_true',
                    dest='prepend_model_name', default=False, help='Prepend '
                    'the model name to the field name'),

        make_option('--categories', action='store_true',
                    dest='categories', default=False, help='Create/link '
                    'categories for each model and associate contained '
                    'fields and concepts.'),
    )

    # These are ignored since these join fields will be determined at runtime
    # using the modeltree library. fields can be created for any other
    # these field types manually
    key_field_types = (
        AutoField,
        ForeignKey,
        OneToOneField,
    )

    def handle(self, *args, **options):
        "Handles app_label or app_label.model_label formats."

        if not args:
            # TODO: this should technically retrieve the subcommand name from
            # the avocado management command class
            self.print_help(sys.argv[0], 'init')
            return

        if options.get('quiet'):
            self.stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        if options.get('force'):
            resp = raw_input('Forcing a init will update metadata for '
                             'existing fields. Are you sure you want to do '
                             'this?\n This will overwrite any previous '
                             'changes made. Type "yes" to continue: ')
            if resp.lower() != 'yes':
                print('Initialization operation cancelled')
                return

        for label in args:
            pending_fields = []
            pending_models = []

            toks = label.split('.')
            app_name = model_name = field_name = None

            # Specific field
            if len(toks) == 3:
                app_name, model_name, field_name = toks
            # All fields for a model
            elif len(toks) == 2:
                app_name, model_name = toks
            # All fields for each model in the app
            else:
                app_name = toks[0]

            if model_name:
                model = get_model(app_name, model_name)

                if model is None:
                    print(u'Cannot find model "{0}", skipping...'
                          .format(label))
                    continue

                # Specific field
                if field_name:
                    try:
                        field = model._meta.get_field_by_name(field_name)[0]
                    except FieldDoesNotExist:
                        print(u'Cannot find field "{0}", skipping...'
                              .format(label))
                        continue
                    pending_fields = [(field, model_name, app_name)]

                # No specific field, queue up the model
                else:
                    pending_models.append(model)
            else:
                app = get_app(app_name)
                if app is None:
                    print(u'Cannot find app "{0}", skipping...'.format(label))
                    continue
                pending_models.extend(get_models(app))

            for model in pending_models:
                model_name = model._meta.object_name.lower()

                for field in model._meta.fields:
                    pending_fields.append((field, model_name, app_name))

            added = 0
            updated = 0

            for field_args in pending_fields:
                status = self.handle_field(*field_args, **options)
                if status is True:
                    added += 1
                elif status is False:
                    updated += 1

            if added == 1:
                print(u'1 field added for {0}'.format(label))
            elif added > 1:
                print(u'{0} fields added for {1}'.format(added, label))

            if updated == 1:
                print(u'1 field updated for {0}'.format(label))
            elif updated > 1:
                print(u'{0} fields updated for {1}'.format(updated, label))

        if options.get('quiet'):
            sys.stdout = self.stdout

    def handle_field(self, field, model_name, app_name, **options):
        include_keys = options.get('include_keys')
        force = options.get('force')
        include_non_editable = options.get('include_non_editable')
        prepend_model_name = options.get('prepend_model_name')
        create_concepts = options.get('concepts')
        auto_publish = options.get('publish')
        create_categories = options.get('categories')

        # M2Ms do not make any sense here..
        if isinstance(field, ManyToManyField):
            return

        # Check for primary key, and foreign key fields
        if isinstance(field, self.key_field_types) and not include_keys:
            print(u'({0}) {1}.{2} is a primary or foreign key. Skipping...'
                  .format(app_name, model_name, field.name))
            return

        # Ignore non-editable fields since in most cases they are for
        # managment purposes
        if not field.editable and not include_non_editable:
            print(u'({0}) {1}.{2} is not editable. Skipping...'
                  .format(app_name, model_name, field.name))
            return

        # All but the field name is case-insensitive, do initial lookup
        # to see if it already exists, skip if it does
        lookup = {
            'app_name__iexact': app_name,
            'model_name__iexact': model_name,
            'field_name': field.name,
        }

        # Note, `name` is set below
        kwargs = {
            'description': field.help_text or None,
            'app_name': app_name,
            'model_name': model_name.lower(),
            'field_name': field.name,
        }

        try:
            f = DataField.objects.get(**lookup)
        except DataField.DoesNotExist:
            f = DataField(published=options.get('publish'), **kwargs)

        if f.pk:
            created = False
            if not force:
                print(u'({0}) {1}.{2} already exists. Skipping...'
                      .format(app_name, model_name, field.name))
                return
            # Only overwrite if the source value is not falsy
            f.__dict__.update([(k, v) for k, v in kwargs.items()])
        else:
            created = True

        if not f.name:
            # Use the default unicode representation of the datafield
            if prepend_model_name:
                f.name = unicode(f)
            else:
                f.name = field.verbose_name.title()

        # Update fields with flags
        f.__dict__.update(utils.get_heuristic_flags(field))

        # Create category based on the model name and associate
        # it to the field.
        if create_categories:
            category, _ = DataCategory.objects\
                .get_or_create(name=f.model._meta.verbose_name.title(),
                               published=auto_publish)
            f.category = category
        else:
            category = None

        f.save()

        # Create a concept if one does not already exist for this field
        if create_concepts and not DataConcept.objects\
                .filter(fields=f).exists():

            kwargs = {
                'published': auto_publish,
                'category': category,
            }

            DataConcept.objects.create_from_field(f, **kwargs)

        return created

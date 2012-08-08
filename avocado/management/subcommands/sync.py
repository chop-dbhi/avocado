import os
import sys
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from optparse import make_option
from django.db.models import (get_model, get_models, get_app, AutoField,
    ForeignKey, OneToOneField, ManyToManyField, FieldDoesNotExist)
from django.core.management.base import BaseCommand
from avocado.models import DataField
from avocado.lexicon.models import Lexicon
from avocado.core import utils


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado sync [options...] labels

    DESCRIPTION:

        Finds all models referenced by the app, model or field `labels` and
        attempts to create a `DataField` instance per model field.
        Any `DataField` already loaded will not be altered in any way.

    OPTIONS:

        `--include-non-editable` - Create `DataField` instances for fields
        marked as not editable (i.e. `editable=False`).

        `--include-keys` - Create `DataField` instances for primary key
        and foreign key fields.

        `--update` - Updates existing `DataField` instances with metadata from
        model fields. Note this overwrites any descriptive metadata changes made
        to `DataField` such as `name`, `name_plural`, and `description`.
    """

    help = '\n'.join([
        'Finds all models referenced by the app, model or field `labels` and',
        'attempts to create a `DataField` instance per model field.',
        'Any `DataField` already loaded will not be altered in any way.'
    ])

    args = 'app [app.model, [app.model.field, [...]]]'

    option_list = BaseCommand.option_list + (
        make_option('-e', '--include-non-editable', action='store_true',
            dest='include_non_editable', default=False,
            help='Create fields for non-editable fields'),

        make_option('-k', '--include-keys', action='store_true',
            dest='include_keys', default=False,
            help='Create fields for primary and foreign key fields'),

        make_option('-u', '--update', action='store_true',
            dest='update_existing', default=False,
            help='Updates existing metadata derived from model fields'),
        make_option('-q', '--quiet', action='store_true',
            dest='quiet', default=False,
            help='Do not print any output')
    )

    # These are ignored since these join fields will be determined at runtime
    # using the modeltree library. fields can be created for any other
    # these field types manually
    key_field_types = (
        AutoField,
        ForeignKey,
        OneToOneField,
    )

    ignored_lexicon_fields = ('order', 'label', 'code')

    def handle(self, *args, **options):
        "Handles app_label or app_label.model_label formats."

        if options.get('quiet'):
            sys.stdout = open(os.devnull, 'w')

        if options.get('update_existing'):
            resp = raw_input('Are you sure you want to update existing metadata?\n'
                'This will overwrite any previous changes made. Type "yes" to continue: ')
            if resp.lower() != 'yes':
                print('Sync operation cancelled')
                return

        for label in args:
            fields = []

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
                    print('Cannot find model "{0}", skipping...'.format(label))
                    continue

                if field_name:
                    try:
                        field = model._meta.get_field_by_name(field_name)[0]
                    except FieldDoesNotExist:
                        print('Cannot find field "{0}", skipping...'.format(label))
                        continue
                    fields = [(field, model_name, app_name)]
                else:
                    lexicon = issubclass(model, Lexicon)
                    for field in model._meta.fields:
                        if lexicon and field.name in self.ignored_lexicon_fields:
                            continue
                        fields.append((field, model_name, app_name))
            else:
                app = get_app(app_name)
                if app is None:
                    print('Cannot find app "{0}", skipping...'.format(label))
                    continue

                for model in get_models(app):
                    lexicon = issubclass(model, Lexicon)
                    model_name = model._meta.object_name.lower()
                    for field in model._meta.fields:
                        if lexicon and field.name in self.ignored_lexicon_fields:
                            continue
                        fields.append((field, model_name, app_name))

            added = 0
            updated = 0
            for field_args in fields:
                status = self.handle_field(*field_args, **options)
                if status is True:
                    added += 1
                elif status is False:
                    updated += 1

            if added == 1:
                print('1 field added for {0}'.format(model_name))
            elif added > 1:
                print('{0:,} fields added for {1}'.format(added, model_name))

            if updated == 1:
                print('1 field updated for {0}'.format(model_name))
            elif updated > 1:
                print('{0:,} fields updated for {1}'.format(updated, model_name))

    def handle_field(self, field, model_name, app_name, **options):
        include_non_editable = options.get('include_non_editable')
        include_keys = options.get('include_keys')
        update_existing = options.get('update_existing')

        if isinstance(field, ManyToManyField):
            return

        # Check for primary key, and foreign key fields
        if isinstance(field, self.key_field_types) and not include_keys:
            return

        # Ignore non-editable fields since in most cases they are for
        # managment purposes
        if not field.editable and not include_non_editable:
            return

        # All but the field name is case-insensitive, do initial lookup
        # to see if it already exists, skip if it does
        lookup = {
            'app_name__iexact': app_name,
            'model_name__iexact': model_name,
            'field_name': field.name,
        }

        kwargs = {
            'name': field.verbose_name.title(),
            'description': field.help_text or None,
            'app_name': app_name.lower(),
            'model_name': model_name.lower(),
            'field_name': field.name,
        }

        try:
            datafield = DataField.objects.get(**lookup)
        except DataField.DoesNotExist:
            datafield = DataField(published=False, **kwargs)

        if datafield.pk:
            created = False
            if not update_existing:
                print('({}) {}.{} already exists. Skipping...'.format(app_name, model_name, field.name))
                return
            # Only overwrite if the source value is not falsy
            datafield.__dict__.update([(k, v) for k, v in kwargs.items()])
        else:
            created = True

        # Update fields with flags
        datafield.__dict__.update(utils.get_heuristic_flags(datafield))
        datafield.save()
        return created

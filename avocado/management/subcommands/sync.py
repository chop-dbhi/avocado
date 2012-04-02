from optparse import make_option
from django.db.models import (get_model, get_models, get_app, AutoField,
    ForeignKey, OneToOneField, ManyToManyField)
from django.core.management.base import LabelCommand
from avocado.models import DataField

class Command(LabelCommand):
    """
    SYNOPSIS::

        python manage.py avocado sync [options...] labels...

    DESCRIPTION:

        Finds all models referenced by the app or model ``labels`` and
        attempts to create a ``DataField`` instance per model field.
        Any ``DataField`` already loaded will not be altered in any way.

    OPTIONS:

        ``--include-non-editable`` - Create ``DataField`` instances for fields marked
        as not editable (i.e. ``editable=False``).

        ``--include-keys`` - Create ``DataField`` instances for primary key
        and foreign key fields.

        ``--update`` - Updates existing ``DataField`` instances with metadata from
        model fields. Note this overwrites any descriptive metadata changes made
        to ``DataField`` such as ``name``, ``name_plural``, and ``description``.

    """

    help = '\n'.join([
        'Finds all models in the listed app(s) and attempts to create a',
        '``DataField`` instance per model field. Fields already declared will',
        'not be altered.'
    ])

    args = 'app [app.model, [...]]'

    option_list = LabelCommand.option_list + (
        make_option('--include-non-editable', action='store_true',
            dest='include_non_editable', default=False,
            help='Create fields for non-editable fields'),

        make_option('--include-keys', action='store_true',
            dest='include_keys', default=False,
            help='Create fields for primary and foreign key fields'),

        make_option('--update', action='store_true',
            dest='update_existing', default=False,
            help='Updates existing metadata derived from model fields'),
    )

    # these are ignored since these join fields will be determined at runtime
    # using the modeltree library. fields can be created for any other
    # these field types manually
    key_field_types = (
        AutoField,
        ForeignKey,
        OneToOneField,
    )

    def handle_label(self, label, **options):
        "Handles app_label or app_label.model_label formats."
        labels = label.split('.')
        models = None
        include_non_editable = options.get('include_non_editable')
        include_keys = options.get('include_keys')
        update_existing = options.get('update_existing')

        if update_existing:
            resp = raw_input('Are you sure you want to update existing metadata?\n'
                'This will overwrite any previous changes made. Type "yes" to continue: ')
            if resp.lower() != 'yes':
                print 'Sync operation cancelled'
                return

        # a specific model is defined
        if len(labels) == 2:
            # attempts to find the model given the app and model labels
            model = get_model(*labels)

            if model is None:
                print 'Cannot find model "%s", skipping...' % label
                return

            models = [model]

        # get all models for the app
        else:
            app = get_app(*labels)
            models = get_models(app)

            if models is None:
                print 'Cannot find app "%s", skipping...' % label
                return

        app_name = labels[0]

        for model in models:
            new_count = 0
            update_count = 0
            model_name = model._meta.object_name.lower()

            for field in model._meta.fields:
                if isinstance(field, ManyToManyField):
                    continue

                # Check for primary key, and foreign key fields
                if isinstance(field, self.key_field_types) and not include_keys:
                    continue

                # Ignore non-editable fields since in most cases they are for
                # managment purposes
                if not field.editable and not include_non_editable:
                    continue

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
                    field_obj = DataField.objects.get(**lookup)
                except DataField.DoesNotExist:
                    field_obj = DataField(published=False, **kwargs)
                    new_count += 1

                if field_obj.pk:
                    if not update_existing:
                        print '(%s) %s.%s already exists. Skipping...' % (app_name, model_name, field.name)
                        continue
                    # Only overwrite if the source value is not falsy
                    field_obj.__dict__.update([(k, v) for k, v in kwargs.items()])
                    update_count += 1

                field_obj.save()


            if new_count == 1:
                print '1 field added for %s' % model_name
            elif new_count > 1:
                print '%d fields added for %s' % (new_count, model_name)

            if update_count == 1:
                print '1 field updated for %s' % model_name
            elif update_count > 1:
                print '%d fields updated for %s' % (update_count, model_name)

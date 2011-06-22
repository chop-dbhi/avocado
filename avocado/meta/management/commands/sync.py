from optparse import make_option

from django.db import models
from django.core.management.base import LabelCommand

from avocado.meta.models import Definition, Domain

class Command(LabelCommand):
    """Finds all models in the listed app(s) and attempts to create a
    ``Definition`` instance per model field. Definitions already declared will
    not be altered.

    Usage::

        python manage.py syncdefinitions <app app.model ...>

    Options:

        ``--create-domains`` - create a single ``Domain`` corresponding to each
        model that is evaluated

        ``--include-non-editable`` - creates Definitions for fields that are not
        editable in the admin

    """

    help = """Finds all models in the listed app(s) and attempts to create a
    ``Definition`` instance per model field. Definitions already declared will
    not be altered.
    """

    args = '<app app app.model ...>'

    option_list = LabelCommand.option_list + (
        make_option('--create-domains', action='store_true',
            dest='create_domains', default=False,
            help='Create a domain for each model'),

        make_option('--include-non-editable', action='store_true',
            dest='include_non_editable', default=False,
            help='Create definitions for non-editable fields')
    )

    # these are ignored since these join fields will be determined at runtime
    # using the modeltree library. definitions can be created for any other
    # these field types manually
    ignored_field_types = (
        models.AutoField,
        models.ForeignKey,
        models.OneToOneField,
        models.ManyToManyField,
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._domains = {}

    def _get_domain(self, model):
        if self._domains.has_key(model):
            domain = self._domains[model]
        else:
            domain, is_new = Domain.objects.get_or_create(name=model._meta.verbose_name)
            self._domains[model] = domain
        return domain

    def handle_label(self, label, **options):
        "Handles app_label or app_label.model_label formats."
        labels = label.split('.')
        mods = None
        create_domains = options.get('create_domains')
        include_non_editable = options.get('include_non_editable')

        # a specific model is defined
        if len(labels) == 2:
            # attempts to find the model given the app and model labels
            model = models.get_model(*labels)

            if model is None:
                print 'Cannot find model "%s", skipping...' % label
                return

            mods = [model]

        # get all models for the app
        else:
            app = models.get_app(*labels)
            mods = models.get_models(app)

            if mods is None:
                print 'Cannot find app "%s", skipping...' % label
                return

        app_name = labels[0]

        for model in mods:
            cnt = 0
            model_name = model._meta.object_name.lower()

            if create_domains:
                domain = self._get_domain(model)

            for field in model._meta.fields:
                # in most cases the primary key fields and non-editable will not
                # be necessary. editable usually include timestamps and such
                if isinstance(field, self.ignored_field_types):
                    continue

                # ignore non-editable fields since in most cases they are for
                # managment purposes
                if not field.editable and not include_non_editable:
                    continue

                kwargs = {
                    'app_name': app_name.lower(),
                    'model_name': model_name,
                    'field_name': field.name,
                }

                # do initial lookup to see if it already exists, skip if it does
                if Definition.objects.filter(**kwargs).exists():
                    print '%s.%s already exists. Skipping...' % (model_name, field.name)
                    continue

                # add verbose name
                kwargs['name'] = field.verbose_name.title()

                definition = Definition(**kwargs)

                if create_domains:
                    definition.domain = domain

                definition.published = False
                definition.save()

                cnt += 1

            if cnt == 1:
                print '1 definition added for %s' % model_name
            else:
                print '%d definitions added for %s' % (cnt, model_name)



from optparse import make_option

from django.core.management.base import LabelCommand
from django.db import models

from avocado.models import Field, Category
from avocado.utils.camel import uncamel

class Command(LabelCommand):
    help = """
        Finds all models in the provided app(s) and attempts to populate
        the table of Field objects. Fields on the model that already exist will
        not be touched."""

    args = '(<app_name.model_name> | <app_name>)+'
    label = '<app_name.model_name> | <app_name>'

    option_list = LabelCommand.option_list + (
        make_option('--no-categories', action='store_false',
            dest='use_categories', default=True,
            help='Do not create categories.'),
    )

    ignored_field_types = (models.AutoField, models.ManyToManyField,
        models.OneToOneField, models.ForeignKey)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._categories = {}

    def _get_category(self, model_name):
        if self._categories.has_key(model_name):
            category = self._categories[model_name]
        else:
            category, is_new = Category.objects.get_or_create(name=uncamel(model_name))
            self._categories[model_name] = category
        return category

    def handle_label(self, label, **options):
        "Handles and `app_label' or `app_label'.`model_label' formats."
        labels = label.split('.')
        mods = None
        use_categories = options.get('use_categories')

        if len(labels) == 2:
            model = models.get_model(*labels)
            if model is None:
                print 'Cannot find model "%s", skipping...' % label
                return
            mods = [model]
        else:
            app = models.get_app(*labels)
            mods = models.get_models(app)
            if mods is None:
                print 'Cannot find app "%s", skipping...' % label
                return

        app_name = labels[0]

        for model in mods:
            cnt = 0

            model_name = model.__name__

            if use_categories:
                category = self._get_category(model_name)

            for field in model._meta.fields:
                # in most cases the primary key fields and non-editable will not
                # be necessary. editable usually include timestamps and such
                if isinstance(field, self.ignored_field_types) or not field.editable:
                    continue

                kwargs = {
                    'app_name': app_name.lower(),
                    'model_name': model_name.lower(),
                    'field_name': field.name,
                }

                # do initial lookup to see if it already exists, skip if it does
                if Field.objects.filter(**kwargs).exists():
                    print '%s.%s already exists. Skipping...' % (model_name, field.name)
                    continue

                # add derived name
                kwargs['name'] = field.name.replace('_', ' ').title()

                model_field = Field(**kwargs)

                if use_categories:
                    model_field.category = category

                model_field.is_public = False
                model_field.save()

                cnt += 1

            if cnt == 1:
                print '1 field added for %s' % model_name
            else:
                print '%d fields added for %s' % (cnt, model_name)


from django.core.management.base import AppCommand
from django.db.models import get_models, AutoField, ManyToManyField, ForeignKey

from avocado.models import FieldConcept, ConceptCategory

class Command(AppCommand):
    help = """Finds all models in the provided app(s) and attempts to populate
        the table of Field objects. Fields on the model that already exist will not
        be touched.
        """

    def handle_app(self, app, **options):
        package_name = app.__package__.split('.', 1)[0]
        models = get_models(app)

        default_category, is_new = ConceptCategory.objects.get_or_create(name='Uncategorized')

        for model in models:
            cnt = 0

            for field in model._meta.fields:
                # in most cases the primary key fields and non-editable will not
                # be necessary. editable usually include timestamps and the such
                if isinstance(field, AutoField) or isinstance(field, ManyToManyField) or \
                    isinstance(field, ForeignKey) or not field.editable:
                    continue

                kwargs = {
                    'model_label': '%s.%s' % (package_name, model.__name__),
                    'field_name': field.name,
                }

                # do initial lookup to see if it already exists, skip if it does
                if FieldConcept.objects.filter(**kwargs).count() > 0:
                    print '%s.%s already exists. Skipping...' % (model.__name__, field.name)
                    continue

                field_concept = FieldConcept(**kwargs)
                field_concept.field_class = field.__class__.__name__
                field_concept.category = default_category
                field.is_public = False
                field_concept.save()

                cnt += 1

            print '%d field(s) added for %s\n' % (cnt, model.__name__)


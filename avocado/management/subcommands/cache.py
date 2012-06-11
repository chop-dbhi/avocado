import sys
from django.conf import settings
from django.db.models import Q
from django.core.management.base import BaseCommand
from avocado.models import DataField


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado cache [options...] labels...

    DESCRIPTION:

        Finds all models referenced by the app or model ``labels`` and
        explicitly updates various cached properties relative to the
        `data_modified` on ``DataField`` instances.
    """

    help = '\n'.join([
        'Finds all models referenced by the app or model ``labels`` and',
        'explicitly updates various cached properties relative to the',
        '`data_modified` on ``DataField`` instances.',
    ])

    args = 'app [app.model, [app.model.field, [...]]]'

    def handle(self, *args, **options):
        "Handles app_label or app_label.model_label formats."
        conditions = []

        for label in args:
            labels = label.split('.')

            # Specific field
            if len(labels) == 3:
                app, model, field = labels
                conditions.append(Q(app_name=app, model_name=model, field_name=field))
            # All fields for a model
            elif len(labels) == 2:
                app, model = labels
                conditions.append(Q(app_name=app, model_name=model))
            # All fields for each model in the app
            else:
                app = labels[0]
                conditions.append(Q(app_name=app))

        q = Q()
        for x in conditions:
            q = q | x
        fields = DataField.objects.filter(q, enumerable=True).distinct()

        count = 0
        for datafield in fields:
            datafield.values
            datafield.size
            if 'avocado.coded' in settings.INSTALLED_APPS:
                datafield.coded_values
            sys.stdout.write('.')
            count += 1

        print '\n{} DataFields have been updated'.format(count)

from datetime import datetime
from optparse import make_option
from django.db.models import Q
from django.core.management.base import BaseCommand
from avocado.models import DataField


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado data [options...] labels...

    DESCRIPTION:

        Finds all models referenced by the app, model or field `labels` and
        updates data-related properties such as caches and pre-calculated
        values.

    OPTIONS:

        `--modified` - Updates the `data_modified` on `DataField` instances
        corresponding the labels. This is primarily used for cache
        invalidation.
    """

    help = '\n'.join([
        'Finds all models referenced by the app, model or field `labels` and',
        'updates data-related properties such as caches and pre-calculated',
        'values.',
    ])

    args = 'app [app.model, [app.model.field, [...]]]'

    option_list = BaseCommand.option_list + (
        make_option('-m', '--modified', action='store_true',
            dest='update_data_modified', default=False,
            help='Update `data_modified` timestamp on `DataField` instances'),
    )

    def handle(self, *args, **options):
        "Handles app_label or app_label.model_label formats."

        update_data_modified = options['update_data_modified']

        if not update_data_modified:
            print 'Nothing to do.'
            return

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

        fields = DataField.objects.all()
        if conditions:
            q = Q()
            for x in conditions:
                q = q | x
            fields = DataField.objects.filter(q)
        updated = fields.update(data_modified=datetime.now())
        print '{} DataFields have been updated'.format(updated)

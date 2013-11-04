from django.db.models import Q
from avocado.models import DataField


def get_fields_by_label(labels):
    """Constructs a DataField QuerySet given a list of labels.

    The label format can be <app>, <app.model> or <app.model.field>.
    """
    conditions = []

    for label in labels:
        labels = label.split('.')

        # Specific field
        if len(labels) == 3:
            app, model, field = labels
            conditions.append(Q(app_name=app, model_name=model,
                                field_name=field))
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
        fields = fields.filter(q).distinct()

    return fields

from copy import deepcopy
from django.db import models


def _validate_field(f):
    "Check if the field is supported for versioning."
    if f.primary_key:
        raise TypeError('Primary keys cannot be versioned.')
    if isinstance(f, (models.ManyToManyField, models.ForeignKey)):
        raise TypeError('Relational fields cannot be versioned.')
    if not f.editable:
        raise TypeError('Non-editable cannot be versioned.')
    return f


def get_object_data(instance, fields):
    "Returns a dict of field data."
    data = {}
    for name in fields:
        _validate_field(instance._meta.get_field(name))
        data[name] = deepcopy(getattr(instance, name))
    return data


def get_model_fields(model):
    "Returns a list of valid fields for versioning."
    fields = []
    for f in model._meta.local_fields:
        # No primary key
        if f is model._meta.pk:
            continue
        # No non-editable fields
        if not f.editable:
            continue
        # No relational fields
        if isinstance(f, (models.ForeignKey, models.ManyToManyField)):
            continue
        fields.append(f.name)
    return fields


def validate_fields(model, fields, exclude):
    "Validates all fields exist and are supported for versioning."
    fields = fields or []
    exclude = exclude or []

    for name in list(fields) + list(exclude):
        _validate_field(model._meta.get_field(name))

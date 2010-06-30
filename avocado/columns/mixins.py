from django.db import models

from avocado.settings import settings
from avocado.utils.mixins import create_mixin
from avocado.columns.formatters import library

fields = {}
for name in settings.VIEW_TYPES.keys():
    fields[name] = models.CharField(max_length=100,
        choices=library.choices(name))

ColumnConceptMixin = create_mixin('ColumnConceptMixin', __name__, fields)
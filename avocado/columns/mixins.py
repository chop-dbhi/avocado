from django.db import models

from avocado.settings import settings
from avocado.utils.mixins import create_mixin
from avocado.columns.fmtlib import library

fields = {}
for name in library.format_types:
    fn = settings.FORMATTER_FIELD_SUFFIX % name
    fields[fn] = models.CharField('%s formatter' % name, max_length=100,
        choices=library.choices(name))

ColumnConceptMixin = create_mixin('ColumnConceptMixin', __name__, fields)
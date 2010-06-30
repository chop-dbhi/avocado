from django.db import models

from avocado.settings import settings
from avocado.utils.mixins import create_mixin
from avocado.criteria.views import library

fields = {}
for name in settings.VIEW_TYPES.keys():
    fields[name] = models.CharField(max_length=100,
        choices=library.choices(name))

CriterionConceptMixin = create_mixin('CriterionConceptMixin', __name__, fields)
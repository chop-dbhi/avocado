from django.db import models

from avocado.settings import settings
from avocado.utils.mixins import create_mixin
from avocado.criteria.viewset import library

fields = {}
for name in library.view_types:
    fn = settings.VIEW_FIELD_SUFFIX % name    
    fields[fn] = models.CharField(max_length=100,
        choices=library.choices(name), null=True, blank=True)

CriterionConceptMixin = create_mixin('CriterionConceptMixin', __name__, fields)
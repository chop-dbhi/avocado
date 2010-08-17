from django.db import models
from django.db.models import Q

from avocado.conf import settings

class FieldManager(models.Manager):
    "Adds additional helper methods focused around access and permissions."
    use_for_related_fields = True
    
    def public(self, *args, **kwargs):
        return self.get_query_set().filter(*args, is_public=True, **kwargs)
    
    if settings.FIELD_GROUP_PERMISSIONS:
        def restrict_by_group(self, groups):
            """Returns public concepts that are apart of the specified groups or
            none at all.
            """
            return self.public(Q(groups__isnull=True) |
                Q(groups__in=groups)).distinct()
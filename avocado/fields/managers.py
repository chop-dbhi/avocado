from django.db import models
from django.db.models import Q

from avocado.conf import settings

class FieldManager(models.Manager):
    "Adds additional helper methods focused around access and permissions."
    use_for_related_fields = True

    def get_by_natural_key(self, app_name, model_name, field_name):
        return self.get(app_name=app_name, model_name=model_name,
            field_name=field_name)

    def public(self):
        """Translates to::

            'return all objects that are public and are not associated with a
            group'.
        """
        return self.get_query_set().filter(is_public=True, group=None)

    if settings.FIELD_GROUP_PERMISSIONS:
        def restrict_by_group(self, groups):
            """Translates to::

                'return all objects that are public or are associated with the same
                groups in ``groups``'.
            """
            return self.get_query_set().filter(Q(group=None) | Q(group__in=groups),
                is_public=True).distinct()

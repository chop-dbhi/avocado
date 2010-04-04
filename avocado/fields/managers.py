from django.db import models

class FieldManager(models.Manager):
    def public(self, **kwargs):
        return super(FieldManager, self).filter(is_public=True,
            category__isnull=False, **kwargs)

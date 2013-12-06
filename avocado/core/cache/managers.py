from django.db import models
from .query import CacheQuerySet


class CacheManager(models.Manager):
    def get_query_set(self):
        return CacheQuerySet(self.model)

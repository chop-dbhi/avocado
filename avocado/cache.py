from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.db.models.query import QuerySet

# Cache for 2 weeks
OBJECT_CACHE_SECONDS = getattr(settings, 'OBJECT_CACHE_SECONDS', 60 * 60 * 24 * 7 * 2)

def instance_cache_key(instance):
    opts = instance._meta
    return '%s.%s:%s' % (opts.app_label, opts.module_name, instance.pk)

def post_save_cache(sender, instance, **kwargs):
    cache.set(instance_cache_key(instance), instance, OBJECT_CACHE_SECONDS)

def pre_delete_uncache(sender, instance, **kwargs):
    cache.delete(instance_cache_key(instance))

class CacheQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        pk = None
        for val in ('pk', 'pk__exact', 'id', 'id__exact'):
            if val in kwargs:
                pk = kwargs[val]
                break
        if pk is not None:
            opts = self.model._meta
            key = '%s.%s:%s' % (opts.app_label, opts.module_name, pk)
            obj = cache.get(key)
            if obj is not None:
                self._result_cache = [obj]
        return super(CacheQuerySet, self).filter(*args, **kwargs)


class CacheManager(models.Manager):
    def get_query_set(self):
        return CacheQuerySet(self.model)

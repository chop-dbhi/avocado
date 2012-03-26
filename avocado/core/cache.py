from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.db.models.query import QuerySet

NEVER_EXPIRE = 0
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

def instance_cache_key(instance, label=None, timestamp=None):
    opts = instance._meta
    key = '%s.%s:%s' % (opts.app_label, opts.module_name, instance.pk)
    if label:
        key = '%s-%s' % (key, label)
    if timestamp:
        key = '%s-%s' % (key, timestamp.strftime(DATETIME_FORMAT))
    return key

def cached_property(label, timestamp=None, timeout=NEVER_EXPIRE):
    "Wraps a function and caches the output indefinitely."
    def decorator(func):
        def wrapped(self):
            ts = getattr(self, timestamp) if timestamp else None
            key = instance_cache_key(self, label=label, timestamp=ts)
            data = cache.get(key)
            if key is None:
                data = func(self)
                cache.set(key, data, timeout=timeout)
            return data
        return property(wrapped)
    return decorator

def post_save_cache(sender, instance, **kwargs):
    cache.set(instance_cache_key(instance), instance, timeout=NEVER_EXPIRE)

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


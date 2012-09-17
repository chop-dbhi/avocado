from django.db import models
from django.core.cache import cache
from django.db.models.query import QuerySet

NEVER_EXPIRE = 60 * 60 * 24 * 30 # 30 days
INSTANCE_CACHE_KEY = '{0}.{1}:{2}'


def instance_cache_key(instance, label=None, version=None):
    "Creates a cache key for the instance with an optional label and token."
    opts = instance._meta
    key = INSTANCE_CACHE_KEY.format(opts.app_label, opts.module_name, instance.pk)
    if label:
        key = '{0}-{1}'.format(key, label)
    if version:
        key = '{0}-{1}'.format(key, version)
    return key


def cached_property(label, version=None, timeout=NEVER_EXPIRE):
    "Wraps a function and caches the output indefinitely."
    def decorator(func):
        def wrapped(self):
            # Do not cache non-persisted objects
            if not self.pk:
                return func(self)

            # If this is a function, pass `label' and `self` in as arguments
            if callable(version):
                _version = version(self, label=label)
            else:
                _version = getattr(self, version)
                # Call if a method
                if callable(_version):
                    _version = _version()
            # If no version is defined, the cache cannot be reliably stored
            if _version is None:
                data = func(self)
            else:
                key = instance_cache_key(self, label=label, version=_version)
                data = cache.get(key)
                if data is None:
                    data = func(self)
                    # Don't bother caching if the data is None
                    if data is not None:
                        cache.set(key, data, timeout=timeout)
            return data
        return property(wrapped)
    return decorator


def post_save_cache(sender, instance, **kwargs):
    """General post-save handler for caching model instances. NOTE: This must
    be used in conjunction with the `pre_delete_uncache` since the cache is set
    to never expire.
    """
    cache.set(instance_cache_key(instance), instance, timeout=NEVER_EXPIRE)


def pre_delete_uncache(sender, instance, **kwargs):
    "General post-delete handler for removing cache for model instances."
    cache.delete(instance_cache_key(instance))


# `pk` is used as an alias, so this is constant
PK_LOOKUPS = ['pk', 'pk__exact']


class CacheQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        """For primary-key-based lookups, instances may be cached to prevent
        excessive database hits. If this is a primary-key lookup, the cache
        will be checked and populate the `_result_cache` if available.
        """
        clone = super(CacheQuerySet, self).filter(*args, **kwargs)

        pk = None
        opts = self.model._meta
        pk_name = opts.pk.name

        # Look for `pk` and the actual name of the primary key field
        for key in PK_LOOKUPS + [pk_name, '{0}__exact'.format(pk_name)]:
            if key in kwargs:
                pk = kwargs[key]
                break

        if pk is not None:
            key = INSTANCE_CACHE_KEY.format(opts.app_label, opts.module_name, pk)
            obj = cache.get(key)
            if obj is not None:
                clone._result_cache = [obj]

        return clone


class CacheManager(models.Manager):
    def get_query_set(self):
        return CacheQuerySet(self.model)

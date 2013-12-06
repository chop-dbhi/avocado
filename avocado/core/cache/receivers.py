from django.core.cache import cache
from .model import instance_cache_key, NEVER_EXPIRE


def post_save_cache(sender, instance, **kwargs):
    """General post-save handler for caching model instances. NOTE: This must
    be used in conjunction with the `pre_delete_uncache` since the cache is set
    to never expire.
    """
    cache.set(instance_cache_key(instance), instance, timeout=NEVER_EXPIRE)


def pre_delete_uncache(sender, instance, **kwargs):
    "General post-delete handler for removing cache for model instances."
    cache.delete(instance_cache_key(instance))

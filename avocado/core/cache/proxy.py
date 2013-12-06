import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheProxy(object):
    def __init__(self, func, version, timeout, key_func):
        self.func = func
        self.label = func.__name__
        self.version = version
        self.timeout = timeout
        self.key_func = key_func

    def cache_key(self, instance):
        return self.key_func(instance, label=self.label, version=self.version)

    def _set(self, key, data):
        logger.debug('Compute property cache "{0}"'.format(key))
        if data is not None:
            cache.set(key, data, timeout=self.timeout)
            logger.debug('Set property cache "{0}"'.format(key))

    def get(self, instance):
        key = self.cache_key(instance)
        data = cache.get(key)
        logger.debug('Get property cache "{0}"'.format(key))
        return data

    def get_or_set(self, instance, *args, **kwargs):
        # Reference to prevent the key from being changed mid-execution
        key = self.cache_key(instance)

        data = cache.get(key)
        if data is None:
            data = self.func(instance, *args, **kwargs)
            self._set(key, data)
        return data

    def flush(self, instance):
        "Flushes cached data for this method."
        key = self.cache_key(instance)
        cache.delete(key)
        logger.debug('Delete property cache "{0}"'.format(key))

    def cached(self, instance):
        "Checks if the data is in the cache."
        return self.cache_key(instance) in cache

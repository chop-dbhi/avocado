import logging
from django.core.cache import get_cache
from avocado.conf import settings

logger = logging.getLogger(__name__)


class CacheProxy(object):
    def __init__(self, func, version, timeout, key_func):
        self.func = func
        self.label = func.__name__
        self.version = version
        self.timeout = timeout
        self.key_func = key_func

    def cache_key(self, instance, args=None, kwargs=None):
        return self.key_func(instance, label=self.label, version=self.version,
                             args=args, kwargs=kwargs)

    def _set(self, key, data):
        logger.debug('Compute property cache "{0}"'.format(key))
        cache = get_cache(settings.DATA_CACHE)

        if data is not None:
            cache.set(key, data, timeout=self.timeout)
            logger.debug('Set property cache "{0}"'.format(key))

    def get(self, instance, args=None, kwargs=None):
        key = self.cache_key(instance, args, kwargs)
        cache = get_cache(settings.DATA_CACHE)
        data = cache.get(key)
        logger.debug('Get property cache "{0}"'.format(key))
        return data

    def get_or_set(self, instance, args=None, kwargs=None):
        # Reference to prevent the key from being changed mid-execution
        key = self.cache_key(instance, args, kwargs)

        cache = get_cache(settings.DATA_CACHE)
        data = cache.get(key)

        if data is None:
            if args is None:
                args = ()

            if kwargs is None:
                kwargs = {}

            data = self.func(instance, *args, **kwargs)
            self._set(key, data)

        return data

    def flush(self, instance, args=None, kwargs=None):
        "Flushes cached data for this method."
        key = self.cache_key(instance, args, kwargs)
        cache = get_cache(settings.DATA_CACHE)
        cache.delete(key)
        logger.debug('Delete property cache "{0}"'.format(key))

    def cached(self, instance, args=None, kwargs=None):
        "Checks if the data is in the cache."
        cache = get_cache(settings.DATA_CACHE)
        return self.cache_key(instance, args, kwargs) in cache

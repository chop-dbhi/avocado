import inspect
import logging
from functools import wraps
from django.core.cache import cache

NEVER_EXPIRE = 60 * 60 * 24 * 30  # 30 days
INSTANCE_CACHE_KEY = u'{0}:{1}:{2}'

log = logging.getLogger(__name__)


def instance_cache_key(instance, label=None, version=None):
    "Creates a cache key for the instance with an optional label and token."

    # If this is a function, pass `label' and `self` in as arguments
    if callable(version):
        version = version(instance, label=label)
    elif version is not None:
        _version = getattr(instance, version)
        # Call if a method
        if callable(_version):
            version = _version()
        else:
            version = _version

    # Construct cache key
    opts = instance._meta
    key = INSTANCE_CACHE_KEY.format(opts.app_label, opts.module_name,
                                    instance.pk)

    if version:
        key = u'{0}:{1}'.format(key, version)
    if label:
        key = u'{0}:{1}'.format(key, label)
    return key


class CacheProxy(object):
    def __init__(self, func, version, timeout, key_func):
        self.func = func
        self.func_name = func.__name__
        self.func_self = None
        self.version = version
        self.timeout = timeout
        self.key_func = key_func

    @property
    def cache_key(self):
        if self.func_self is None:
            return
        return self.key_func(self.func_self, self.func_name, self.version)

    def _set(self, key, data):
        log.debug('Compute property cache "{0}" on "{1}"'.format(
            self.func_name, self.func_self))
        if data is not None:
            cache.set(key, data, timeout=self.timeout)
            log.debug('Set property cache "{0}" on "{1}"'.format(
                self.func_name, self.func_self))

    def get(self):
        if self.func_self is None:
            return
        data = cache.get(self.cache_key)
        log.debug('Get property cache "{0}" on "{1}"'.format(self.func_name,
                  self.func_self))
        return data

    def get_or_set(self, *args, **kwargs):
        if self.func_self is None:
            return

        # Reference to prevent the key from being changed mid-execution
        key = self.cache_key

        data = cache.get(key)
        if data is None:
            data = self.func(self.func_self, *args, **kwargs)
            self._set(key, data)
        return data

    def flush(self):
        "Flushes cached data for this method."
        if self.func_self is None:
            return
        cache.delete(self.cache_key)
        log.debug('Delete property cache "{0}" on "{1}"'.format(
            self.func_name, self.func_self))

    def cached(self):
        "Checks if the data is in the cache."
        if self.func_self is None:
            return False
        return self.cache_key in cache


def cached_method(func=None, version=None, timeout=NEVER_EXPIRE,
                  key_func=instance_cache_key):
    "Wraps a method and caches the output indefinitely."
    from avocado.conf import settings

    def decorator(func):
        cache_proxy = CacheProxy(func, version, timeout, key_func)

        @wraps(func)
        def inner(self, *args, **kwargs):
            # This check is here to be ensure transparency of the augmented
            # methods below. The agumented methods will be a no-op since the
            # `func_self` will never be set as long as this condition is true.
            if not settings.DATA_CACHE_ENABLED:
                return func(self, *args, **kwargs)
            if cache_proxy.func_self is None:
                cache_proxy.func_self = self
            return cache_proxy.get_or_set(*args, **kwargs)

        # Augment method with a few methods. These are wrapped in a lambda
        # to prevent mucking the cache_proxy instance directly..
        inner.flush = lambda: cache_proxy.flush()
        inner.cached = lambda: cache_proxy.cached()
        inner.cache_key = lambda: cache_proxy.cache_key

        return inner

    if inspect.isfunction(func):
        return decorator(func)
    return decorator

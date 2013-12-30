import inspect
from functools import wraps
from avocado.conf import settings
from .proxy import CacheProxy

NEVER_EXPIRE = 60 * 60 * 24 * 30  # 30 days
CACHE_KEY_FUNC = lambda l: ':'.join([str(x) for x in l])


def instance_cache_key(instance, label=None, version=None):
    """Creates a cache key for the instance with an optional label and version.
    The instance is uniquely defined based on the app, model and primary key of
    the instance.

    A `label` is used to differentiate cache for an instance.

    The `version` can be a scalar (i.e. a string or int), a function, instance
    property or method.
    """
    if version is None:
        version = '-'
    elif callable(version):
        version = version(instance, label=label)
    elif hasattr(instance, version):
        version = getattr(instance, version)
        if callable(version):
            version = version()

    opts = instance._meta
    key = [opts.app_label, opts.module_name, instance.pk, version]

    if label is not None:
        key.append(label)

    return CACHE_KEY_FUNC(key)


def cached_method(func=None, version=None, timeout=NEVER_EXPIRE,
                  key_func=instance_cache_key):
    "Wraps a method and caches the output indefinitely."

    def decorator(func):
        # Single cache proxy shared across all instances. All methods require
        # the instance to be passed.
        cache_proxy = CacheProxy(func, version, timeout, key_func)

        @wraps(func)
        def inner(self, *args, **kwargs):
            # This check is here to be ensure transparency of the augmented
            # methods below. The agumented methods will be a no-op since the
            # `func_self` will never be set as long as this condition is true.
            if not settings.DATA_CACHE_ENABLED or args or kwargs:
                return func(self, *args, **kwargs)
            return cache_proxy.get_or_set(self, *args, **kwargs)

        # Augment method with a few methods. These are wrapped in a lambda
        # to prevent mucking the cache_proxy instance directly..
        inner.flush = lambda i: cache_proxy.flush(i)
        inner.cached = lambda i: cache_proxy.cached(i)
        inner.cache_key = lambda i: cache_proxy.cache_key(i)

        return inner

    if inspect.isfunction(func):
        return decorator(func)
    return decorator

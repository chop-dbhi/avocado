import inspect
import hashlib
import logging
import cPickle as pickle
from django.db.models.query import QuerySet
from functools import wraps
from avocado.conf import settings
from .proxy import CacheProxy

NEVER_EXPIRE = 60 * 60 * 24 * 30  # 30 days


logger = logging.getLogger(__name__)


def _pickling_value(v):
    "Returns an appropriate value to be pickled."
    if isinstance(v, QuerySet):
        # Compile the query and use the SQL string as the pickle value.
        # Microbenchmarking shows this is faster than pickling and then
        # hashing the query's internal dict. In addition, the variability
        # in SQL queries vs. the internal structure of query across Django
        # versions is at most the same if not less variable.
        s, p = v.query.get_compiler(v.db).as_sql()

        return s % p

    if inspect.isclass(v) and not hasattr(v, '__getstate__'):
        # As with the QuerySet instance above, this could result in loading
        # a lot of data into memory.
        logger.warn('type "{0}" does not implement __getstate__'
                    .format(type(v)))

    return v


def _prep_pickling(args, kwargs):
    "Prepares the positional and keyword arguments for pickling."
    if args:
        args = [_pickling_value(v) for v in args]
    else:
        args = None

    _kwargs = {}

    if kwargs:
        for k, v in kwargs.items():
            if v is not None:
                _kwargs[k] = _pickling_value(v)

        kwargs = _kwargs or None
    else:
        kwargs = None

    return args, kwargs


def cache_key_func(l):
    "Computes a hashed cache key from a list of values."
    raw = ':'.join([str(x) for x in l])
    return hashlib.sha256(raw).hexdigest()


def cache_key(label, version=None, args=None, kwargs=None):
    """Creates a cache key given label and optional version.

    In addition, arbitrary arguments and keyword arguments may be passed that
    will be pickled prior to being included in the cache key. This is useful
    for caching return values from functions that take arguments.
    """
    if not label:
        raise ValueError('cache label cannot be empty')

    if version is None:
        version = '-'
    elif callable(version):
        version = version()

    key = [label, version]

    args, kwargs = _prep_pickling(args, kwargs)

    if args or kwargs:
        key.append(pickle.dumps((args, kwargs)))

    return cache_key_func(key)


def instance_cache_key(instance, label=None, version=None, args=None,
                       kwargs=None):
    """Extends the base `cache_key` function to include model instance metadata
    such as the type and primary key. In addition the `version` can be a
    property or method name on the instance which will be evaluated.
    """
    if not instance or not instance.pk:
        raise ValueError('model instances must have a primary key')

    # The version may be an attribute on the instance
    if isinstance(version, basestring) and hasattr(instance, version):
        version = getattr(instance, version)

        # Bound method
        if callable(version):
            version = version()

    # Plain function takes the instance
    elif callable(version):
        version = version(instance)

    opts = instance._meta
    key = [opts.app_label, opts.module_name, instance.pk]

    if label is not None:
        key.append(label)

    label = cache_key_func(key)

    return cache_key(label=label, version=version, args=args, kwargs=kwargs)


def cached_method(func=None, version=None, timeout=NEVER_EXPIRE,
                  key_func=instance_cache_key):
    "Wraps a model instance method and caches the output indefinitely."

    def decorator(func):
        # Single cache proxy shared across all instances. All methods require
        # the instance to be passed.
        cache_proxy = CacheProxy(func, version, timeout, key_func)

        @wraps(func)
        def inner(self, *args, **kwargs):
            # This check is here to be ensure transparency of the augmented
            # methods below. The agumented methods will be a no-op since the
            # `func_self` will never be set as long as this condition is true.
            if not settings.DATA_CACHE_ENABLED:
                return func(self, *args, **kwargs)

            return cache_proxy.get_or_set(self, args=args, kwargs=kwargs)

        def flush(instance, args=None, kwargs=None):
            return cache_proxy.flush(instance, args, kwargs)

        def cached(instance, args=None, kwargs=None):
            return cache_proxy.cached(instance, args, kwargs)

        def cache_key(instance, args=None, kwargs=None):
            return cache_proxy.cache_key(instance, args, kwargs)

        inner.flush = flush
        inner.cached = cached
        inner.cache_key = cache_key

        return inner

    if inspect.isfunction(func):
        return decorator(func)
    return decorator

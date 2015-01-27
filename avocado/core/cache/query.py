from django.core.cache import get_cache
from django.db.models.query import QuerySet
from avocado.conf import settings
from .model import cache_key_func

PK_LOOKUPS = ('pk', 'pk__exact')


class CacheQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        """For primary-key-based lookups, instances may be cached to prevent
        excessive database hits. If this is a primary-key lookup, the cache
        will be checked and populated in the `_result_cache` if available.
        """
        clone = super(CacheQuerySet, self).filter(*args, **kwargs)

        pk = None
        opts = self.model._meta
        pk_name = opts.pk.name

        # Look for `pk` and the actual name of the primary key field
        for key in list(PK_LOOKUPS) + [pk_name, u'{0}__exact'.format(pk_name)]:
            if key in kwargs:
                pk = kwargs[key]
                break

        if pk is not None:
            key = cache_key_func([opts.app_label, opts.module_name, pk])
            cache = get_cache(settings.DATA_CACHE)
            obj = cache.get(key)

            if obj is not None:
                clone._result_cache = [obj]

        return clone

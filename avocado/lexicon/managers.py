from django.db import models


def coerce_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return x

key_funcs = {
    'coerce_float': coerce_float,
}


class LexiconManager(models.Manager):
    def reorder(self, cmp=None, key=None):
        if isinstance(key, basestring):
            if key not in key_funcs:
                raise KeyError('No key function named {0}'.format(key))
            key = key_funcs[key]
        items = list(self.get_query_set())
        items.sort(cmp=cmp, key=key)
        for i, item in enumerate(items):
            item.order = i
            item.save()

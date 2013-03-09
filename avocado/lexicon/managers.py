from django.db import models, transaction


def coerce_float(x):
    try:
        return float(x.value)
    except (TypeError, ValueError):
        return x.value

key_funcs = {
    'coerce_float': coerce_float,
}


class LexiconManager(models.Manager):
    @transaction.commit_on_success
    def reorder(self, cmp=None, key=None, reverse=False):
        if isinstance(key, basestring):
            if key not in key_funcs:
                raise KeyError(u'No key function named {0}'.format(key))
            key = key_funcs[key]

        items = list(self.get_query_set())
        items.sort(cmp=cmp, key=key, reverse=reverse)

        for i, item in enumerate(items):
            item.order = i
            item.save()

from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache as _cache

from avocado.fields.models import Field

class FieldCache(object):
    def __init__(self, class_name):
        self.id_key = ':'.join(['avocado', class_name, '%s'])
        self.label_key = ':'.join(['avocado', class_name, '%s', '%s', '%s'])
        self.field_id_key = ':'.join(['avocado', class_name, '%s', 'fields'])
        self.field_label_key = ':'.join(['avocado', class_name, '%s', '%s', '%s', 'fields'])
    
    def get(self, field_id=None, app_name=None, model_name=None, field_name=None, queryset=None, ret_val=None):
        "Simple interface for getting (and setting) a field from global cache."
        if not field_id and not (app_name and model_name and field_name):
            raise RuntimeError, 'not enough lookup params defined'

        if queryset is None:
            queryset = Field.objects.all()

        if field_id:
            key = self.id_key % field_id
            kwargs = {'id': field_id}
        else:
            key = self.label_key % (app_name, model_name, field_name)
            kwargs = {'app_name': app_name, 'model_name': model_name,
                'field_name': field_name}

        field = _cache.get(key, None)
        if field is None:
            try:
                field = queryset.get(**kwargs)
            except ObjectDoesNotExist:
                return ret_val
            # create other key and set a reference to the object for both keys
            if field_id:
                skey = self.label_key % (field.app_name, field.model_name,
                    field.field_name)
            else:
                skey = self.id_key % field.id

            _cache.set(key, field)
            _cache.set(skey, field)

        return field

    def get_many(self, ids_or_labels, queryset=None):
        "Returns a generator of field objects."
        for args in iter(ids_or_labels):
            if type(args) is int or str(args).isdigit():
                yield self.get(args, queryset=queryset)
            else:
                yield self.get(None, *args, queryset=queryset)


cache = FieldCache(Field.__name__.lower())

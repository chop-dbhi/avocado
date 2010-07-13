from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache as _cache

from avocado.fields.models import FieldConcept

class FieldConceptCache(object):
    def __init__(self, model_name):
        self.id_key = ':'.join(['avocado', model_name, '%s'])
        self.label_key = ':'.join(['avocado', model_name, '%s', '%s'])
        self.field_id_key = ':'.join(['avocado', model_name, '%s', 'fields'])
        self.field_label_key = ':'.join(['avocado', model_name, '%s', '%s', 'fields'])
    
    def get(self, concept_id=None, model_label=None, field_name=None, queryset=None, ret_val=None):
        "Simple interface for getting (and setting) a concept from global cache."
        if not concept_id and not (model_label and field_name):
            raise RuntimeError, 'not enough lookup params defined'

        if queryset is None:
            queryset = FieldConcept.objects.all()

        if concept_id:
            key = self.id_key % concept_id
            kwargs = {'id': concept_id}
        else:
            key = self.label_key % (model_label, field_name)
            kwargs = {'model_label': model_label, 'field_name': field_name}

        concept = _cache.get(key, None)
        if concept is None:
            try:
                concept = queryset.get(**kwargs)
            except ObjectDoesNotExist:
                return ret_val
            # create other key and set a reference to the object for both keys
            if concept_id:
                skey = self.label_key % (concept.model_label, concept.field_name)
            else:
                skey = self.id_key % concept.id

            _cache.set(key, concept)
            _cache.set(skey, concept)

        return concept

    def get_many(self, ids_or_labels, queryset=None):
        "Returns a generator of concept objects."
        for x in iter(ids_or_labels):
            if type(x) is int or str(x).isdigit():
                yield self.get(concept_id=x, queryset=queryset)
            else:
                yield self.get(model_label=x[0], field_name=x[1], queryset=queryset)


cache = FieldConceptCache(FieldConcept.__name__.lower())
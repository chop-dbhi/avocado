import re

from django.db import models
from django.db.models.query_utils import Q

from avocado.settings import settings
from avocado.modeltree import ModelTree
from avocado.fields.models import FieldConcept
from avocado.fields.cache import cache

DEFAULT_MODEL_TREE = None

ID_RE = re.compile(r'\d+')

class AmbiguousFieldName(Exception):
    pass

if settings.MODEL_TREE_MODELS:
    mods = []
    for label in settings.MODEL_TREE_MODELS:
        app_label, model_label = label.split('.')
        mods.append(models.get_model(app_label, model_label))
    DEFAULT_MODEL_TREE = ModelTree(mods.pop(0), exclude=mods)
    del mods

class M(Q):
    model_tree = DEFAULT_MODEL_TREE
    
    def __init__(self, model_tree=None, **kwargs):
        self.model_tree = model_tree or self.model_tree
        if not isinstance(self.model_tree, ModelTree):
            raise RuntimeError, 'A ModelTree instance required'

        nkwargs = {}
        for key, value in kwargs.items():
            toks = key.split('__')
            toks_len = len(toks)
            
            concept = operator = None
            
            # test for special pk syntax, e.g. _100 or _100__gt
            if re.match(r'_\d+', toks[0]):
                if toks_len > 2:
                    raise TypeError, 'invalid pk syntax'
                concept_id = int(toks[0][1:])
                if toks_len == 2:
                    operator = toks[1]
                concept = cache.get(concept_id)
            else:        
                app_label = model_label = field_name = None
                # myfield
                if toks_len == 1:
                    field_name = toks[0]
                # myfield__gt
                elif toks_len == 2:
                    field_name, operator = toks
                # myapp__mymodel__myfield
                elif toks_len == 3:
                    app_label, model_label, field_name = toks
                # myapp__mymodel__myfield__gt
                elif toks_len == 4:
                    app_label, model_label, field_name, operator = toks
    
                concept= self._get_field(field_name, app_label, model_label)
            
            skey = concept.query_string(operator)
            nkwargs[skey] = value

        return super(M, self).__init__(**nkwargs)
    
    def _get_field(self, field_name, app_label=None, model_label=None):
        try:
            if app_label and model_label:
                return FieldConcept.objects.get(field_name=field_name,
                    model_label='.'.join([app_label, model_label]))
            return FieldConcept.objects.get(field_name=field_name)
        except FieldConcept.MultipleObjectsReturned:
            raise AmbiguousFieldName, 'Ambiguous field "%s"'
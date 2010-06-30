from django.db import models
from django.db.models.query_utils import Q

from avocado.settings import settings
from avocado.modeltree import ModelTree
from avocado.fields.models import FieldConcept

DEFAULT_MODEL_TREE = None

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
            
            field_name = operator = app_label = model_label = None
            
            if toks_len == 1:
                field_name = toks[0]
            elif toks_len == 2:
                field_name, operator = toks
            elif toks_len == 3:
                app_label, model_label, field_name = toks
            elif toks_len == 4:
                app_label, model_label, field_name, operator = toks
    
            field = self._get_field(field_name, app_label, model_label)
            query_str = self._expand_path(field, operator)
            
            nkwargs[query_str] = value

        return super(M, self).__init__(**nkwargs)
    
    def _get_field(self, field_name, app_label=None, model_label=None):
        try:
            if app_label and model_label:
                return FieldConcept.objects.get(field_name=field_name,
                    model_label='.'.join([app_label, model_label]))
            return FieldConcept.objects.get(field_name=field_name)
        except FieldConcept.MultipleObjectsReturned:
            raise AmbiguousFieldName, 'Ambiguous field "%s"'

    def _expand_path(self, field, operator=None):
        node_path = self.model_tree.path_to(field.model)
        return self.model_tree.query_string(node_path, field.field_name, operator)
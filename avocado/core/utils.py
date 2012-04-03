from django import forms
from django.utils.importlib import import_module

def get_form_class(name):
    # Absolute import if a period exists, otherwise assume the
    # name refers to a built-in Django class
    if '.' in name:
        path = name.split('.')[:-1]
        module = import_module(path)
    else:
        if not name.endswith('Field'):
            name = name + 'Field'
        module = forms
    return getattr(module, name)

def get_internal_type(field):
    "Get model field internal type with 'field' off."
    datatype = field.get_internal_type().lower()
    if datatype.endswith('field'):
        datatype = datatype[:-5]
    return datatype

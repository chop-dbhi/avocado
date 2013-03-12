from django import forms
from django.db import models
from django.utils.importlib import import_module
from avocado.conf import settings


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

def get_simple_type(field):
    """Returns a simple type mapped from the internal type."

    By default, it will use the field's internal type, but can be
    overridden by the ``SIMPLE_TYPES`` setting.
    """
    internal = get_internal_type(field)
    return settings.SIMPLE_TYPES.get(internal, internal)


def get_heuristic_flags(field):
    # TODO add better conditions for determining how to set the
    # flags for most appropriate interface.
    # - Determine length of MAX value for string-based fields to rather
    # than relying on the `max_length`. This will enable checking TextFields
    # - Numerical fields may be enumerable, check the size of them if an
    # option is set?
    # For strings and booleans, set the enumerable flag by default
    # it below the enumerable threshold
    # TextFields are typically used for free text
    enumerable = False

    if field.internal_type != 'text' and field.simple_type in ('string', 'boolean') \
            and field.size <= settings.ENUMERABLE_MAXIMUM:
        enumerable = True

    return {
        'enumerable': enumerable,
    }


def parse_field_key(key):
    "Returns a field lookup based on a variety of key types."
    if isinstance(key, int):
        return {'pk': key}
    keys = ('app_name', 'model_name', 'field_name')
    if isinstance(key, models.Field):
        opts = key.model._meta
        toks = [opts.app_label, opts.module_name, key.name]
    elif isinstance(key, basestring):
        toks = key.split('.')
    elif isinstance(key, (list, tuple)):
        toks = key
    offset = len(keys) - len(toks)
    return dict(zip(keys[offset:], toks))

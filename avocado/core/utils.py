from django import forms
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
    searchable = False
    enumerable = False

    if field.internal_type == 'text':
        searchable = True
    elif field.simple_type in ('string', 'boolean'):
        if field.size > settings.SYNC_ENUMERABLE_MAXIMUM:
            searchable = True
        else:
            enumerable = True

    return {
        'searchable': searchable,
        'enumerable': enumerable,
    }

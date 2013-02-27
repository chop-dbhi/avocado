from django import forms
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from avocado.conf import settings


def get_form_class(name):
    # Absolute import if a period exists, otherwise assume the
    # name refers to a built-in Django class
    if '.' in name:
        return import_by_path(name)
    if not name.endswith('Field'):
        name = name + 'Field'
    return getattr(forms, name)


def get_internal_type(field):
    "Get model field internal type with 'field' off."
    datatype = field.get_internal_type().lower()
    if datatype.endswith('field'):
        datatype = datatype[:-5]
    return datatype


def get_simple_type(internal):
    """Returns a simple type mapped from the internal type."

    By default, it will use the field's internal type, but can be
    overridden by the ``SIMPLE_TYPES`` setting.
    """
    if isinstance(internal, models.Field):
        internal = get_internal_type(internal)
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
            and field.size() <= settings.ENUMERABLE_MAXIMUM:
        enumerable = True

    return {
        'enumerable': enumerable,
    }


def parse_field_key(key):
    "Returns a field lookup based on a variety of key types."
    if isinstance(key, int):
        return {'pk': key}
    keys = ('app_name', 'model_name', 'field_name')
    if isinstance(key, basestring):
        toks = key.split('.')
    elif isinstance(key, (list, tuple)):
        toks = key
    offset = len(keys) - len(toks)
    return dict(zip(keys[offset:], toks))


# Ported from Django 1.5
def import_by_path(dotted_path, error_prefix=''):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImproperlyConfigured if something goes wrong.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        raise ImproperlyConfigured("%s%s doesn't look like a module path" % (
            error_prefix, dotted_path))
    try:
        module = import_module(module_path)
    except ImportError as e:
        raise ImproperlyConfigured('%sError importing module %s: "%s"' % (
            error_prefix, module_path, e))
    try:
        attr = getattr(module, class_name)
    except AttributeError:
        raise ImproperlyConfigured('%sModule "%s" does not define a "%s" attribute/class' % (
            error_prefix, module_path, class_name))
    return attr

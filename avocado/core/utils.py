from random import choice
from string import ascii_lowercase, digits
from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.utils.importlib import import_module
from avocado.conf import settings


# 41 characters @ 30 characters per username = 3.16 billion permutations
# I think that will cover it..
USERNAME_CHARS = ascii_lowercase + digits + '@.+-_'


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


def get_simple_type(internal):
    """Returns a simple type mapped from the internal type."

    By default, it will use the field's internal type, but can be
    overridden by the ``SIMPLE_TYPES`` setting.
    """
    if isinstance(internal, models.Field):
        internal = get_internal_type(internal)
    return settings.SIMPLE_TYPES.get(internal, internal)


def is_enumerable(field):
    internal_type = get_internal_type(field)
    simple_type = get_simple_type(internal_type)

    if internal_type == 'text' or simple_type not in ('string', 'boolean'):
        return False

    count = field.model.objects.values_list(field.name).distinct().count()
    return count <= settings.ENUMERABLE_MAXIMUM


def is_searchable(field):
    simple_type = get_simple_type(field)
    return simple_type == 'string' and not is_enumerable(field)


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
    enumerable = is_enumerable(field)
    return {
        'enumerable': enumerable,
        'indexable': enumerable or is_searchable(field),
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


def generate_random_username(length=30, max_attempts=100):
    for i in xrange(max_attempts):
        username = ''.join(choice(USERNAME_CHARS) for i in xrange(length))
        if not User.objects.filter(username=username).exists():
            return username
    raise ValueError('Maximum attempts made to generate username')


def create_email_based_user(email):
    """
    Creates an inactive user from the email address. These users are
    placeholders for those users that do not have accounts. This is initially
    planned for use in conjunction with adding users to DataQuery.shared_users.
    """
    username = generate_random_username()
    email = User.objects.normalize_email(email)

    user = User(username=username, email=email, is_active=False)
    user.set_unusable_password()
    user.full_clean()
    user.save()

    return user

from avocado.core import loader
from .models import DataField


field_registry = loader.Registry()


class FieldProfile(object):
    pass


def register_field(key, options):
    f = DataField.init(key)
    if isinstance(options, dict):
        profile = FieldProfile(f)
    else:
        profile = options
        profile.field = f
    field_registry(profile, key)

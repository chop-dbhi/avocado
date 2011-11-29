from django.db import models
from django.utils.importlib import import_module

from avocado.conf import settings
from avocado.utils.mixins import create_mixin
from avocado.columns.format import library

# attempt to import the user-defined mixin class if specified
if settings.COLUMN_MIXIN_PATH is not None:
    path = settings.COLUMN_MIXIN_PATH.split('.')
    mixin_name = path.pop(-1)
    mod = import_module('.'.join(path))
    Mixin = getattr(mod, mixin_name)
else:
    Mixin = models.Model

# XXX ghetto...
default = None
if library.default:
    default = library._get_class_name(library.default.__class__)

fields = {}
for name in settings.FORMATTER_TYPES:
    fn = name + settings.FORMATTER_FIELD_SUFFIX
    fields[fn] = models.CharField('%s formatter' % name, max_length=100,
        choices=sorted(library.choices(name)), default=default)

Mixin = create_mixin('Mixin', __name__, bases=(Mixin,), fields=fields)

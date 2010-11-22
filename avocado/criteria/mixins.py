from django.db import models
from django.utils.importlib import import_module

from avocado.conf import settings

# attempt to import the user-defined mixin class if specified
if settings.CRITERION_MIXIN_PATH is not None:
    path = settings.CRITERION_MIXIN_PATH.split('.')
    mixin_name = path.pop(-1)
    mod = import_module('.'.join(path))
    Mixin = getattr(mod, mixin_name)
else:
    Mixin = models.Model

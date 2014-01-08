import warnings
from avocado.conf import dep_supported, raise_dep_error

if not dep_supported('objectset'):
    raise_dep_error('objectset')

from objectset.models import ObjectSet, SetObject  # noqa

warnings.warn('The built-in ObjectSet and SetObject classes have been '
              'removed in favor of the classes defined in the '
              'django-objectset library. Imports should be changed to '
              'import directly from objectset.models instead of from '
              'avocado.sets.models')

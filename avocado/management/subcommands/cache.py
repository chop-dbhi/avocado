import sys
import time
import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from avocado.models import DataField
from avocado.management.base import DataFieldCommand

log = logging.getLogger(__name__)

# Get all methods that have a `flush` method for clearing the
# internal cache.
CACHED_METHODS = []

for attr_name in dir(DataField):
    attr = getattr(DataField, attr_name)
    # This is crude means of checking for methods that contain a CacheProxy,
    # however that is the only method used below.
    if hasattr(attr, 'flush'):
        CACHED_METHODS.append(attr_name)

CACHED_METHODS = tuple(CACHED_METHODS)


__doc__ = """\
Pre-caches data produced by various DataField methods that are data dependent.
Pass `--flush` to explicitly flush any existing cache for each method.
"""


class Command(DataFieldCommand):
    help = __doc__

    option_list = BaseCommand.option_list + (
        make_option('--flush', action='store_true', help='Flushes existing '
                    'cache for each cached property.'),

        make_option('--methods', action='append', dest='methods',
                    default=CACHED_METHODS, help='Select which methods to '
                    'pre-cache. Choices: {0}'.format(
                        ', '.join(CACHED_METHODS))),
    )

    def _progress(self):
        sys.stdout.write('.')
        sys.stdout.flush()

    def handle_fields(self, fields, **options):
        flush = options.get('flush')
        methods = options.get('methods')

        # Validate methods
        for method in methods:
            if method not in CACHED_METHODS:
                raise CommandError('Invalid method {0}. Choices are {1}'
                                   .format(method, ', '.join(CACHED_METHODS)))

        count = 0
        t0 = time.time()

        for f in fields:
            for method in methods:
                func = getattr(f, method)
                if flush:
                    func.flush(f)
                func()
            count += 1
            self._progress()
            log.debug('{0} cache set took {1} seconds'.format(
                f, time.time() - t0))

        print(u'\n{0} fields have been updated ({1} s)'.format(
            count, round(time.time() - t0, 2)))

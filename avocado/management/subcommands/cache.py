import sys
import time
import logging
from optparse import make_option
from django.db import transaction
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

METHOD_CHOICES = ', '.join(CACHED_METHODS)


__doc__ = """\
Pre-caches data produced by various DataField methods that are data dependent.
Pass `--flush` to explicitly flush any existing cache for each method.
"""


class Command(DataFieldCommand):
    help = __doc__

    option_list = BaseCommand.option_list + (
        make_option('--flush',
                    action='store_true',
                    help='Flushes existing cache for each cached property.',
                    default=False),

        make_option('--methods',
                    action='append',
                    dest='methods',
                    default=CACHED_METHODS,
                    help='Select which methods to pre-cache. Choices: {0}'
                         .format(METHOD_CHOICES)),
    )

    @transaction.commit_on_success
    def _handle_field_method(self, f, method, flush):
        func = getattr(f, method)

        if flush:
            func.flush(f)

        if func.cached(f):
            self.skipped += 1
        else:
            data = func()

            if data is not None:
                self.cached += 1

    def handle_fields(self, fields, **options):
        flush = options.get('flush')
        methods = options.get('methods')

        # Validate methods
        for method in methods:
            if method not in CACHED_METHODS:
                raise CommandError('Invalid method {0}. Choices are {1}'
                                   .format(method, METHOD_CHOICES))

        self.total = 0
        self.skipped = 0
        self.cached = 0
        self.errors = 0

        t0 = time.time()

        for f in fields:
            for method in methods:
                self.total += 1

                # By default, the settings run on sqlite3 DB so a
                # DatabaseError will be triggered when the standard deviation
                # or variance functions are used.
                try:
                    self._handle_field_method(f, method, flush)
                except Exception:
                    self.errors += 1
                    log.exception('error populating cache for "{0}" {1}'
                                  .format(f, method))

            if self.total % 10 == 0:
                sys.stdout.write('\r{0}/{1}/{2}/{3} '
                                 'cached/skipped/errors/total'
                                 .format(self.cached, self.skipped,
                                         self.errors, self.total))
                sys.stdout.flush()

        print('\nTook {0} s'.format(round(time.time() - t0, 2)))

import sys
import time
import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from avocado.management.base import DataFieldCommand

log = logging.getLogger(__name__)


_help = """\
Pre-caches data produced by various DataField methods that are data dependent.

Pass `--flush` to explicitly flush any existing cache for each property.
"""

CACHED_METHODS = ('size', 'values', 'labels', 'codes')

class Command(DataFieldCommand):
    __doc__ = help = _help

    option_list = BaseCommand.option_list + (
        make_option('--flush', action='store_true',
            help='Flushes existing cache for each cached property.'),

        make_option('--method', action='append', dest='methods',
            default=CACHED_METHODS,
            help='Select which methods to pre-cache. Choices: {0}'.format(', '.join(CACHED_METHODS))),
    )

    def _progress(self):
        sys.stdout.write('.')
        sys.stdout.flush()

    def handle_fields(self, fields, **options):
        flush = options.get('flush')
        methods = options.get('methods')

        for method in methods:
            if method not in CACHED_METHODS:
                raise CommandError('Invalid method {0}. Choices are {1}'.format(method, ', '.join(CACHED_METHODS)))

        fields = fields.filter(enumerable=True)

        count = 0
        for f in fields:
            t0 = time.time()
            for method in methods:
                func = getattr(f, method)
                if flush:
                    func.flush()
                func()
                self._progress()
            count += 1
            log.debug('{0} cache set took {1:,} seconds'.format(f, time.time() - t0))

        print(u'{0} DataFields have been updated'.format(count))

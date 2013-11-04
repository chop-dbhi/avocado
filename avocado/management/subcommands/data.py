import logging
from django.db.models import F
from optparse import make_option
from avocado.management.base import DataFieldCommand

log = logging.getLogger(__name__)

__doc__ = """\
Increments the `data_version` field on DataField instances. This will cause
various cache that depends on this field to be refreshed the next time it is
requested. To pre-cache, use the `avocado cache` command.
"""


class Command(DataFieldCommand):
    help = __doc__

    option_list = DataFieldCommand.option_list + (
        make_option('-i', '--incr', action='store_true', dest='incr_version',
                    default=False, help='Increment `data_version` on '
                    '`DataField` instances'),
    )

    def handle_fields(self, fields, **options):
        "Handles app_label or app_label.model_label formats."

        incr_version = options.get('incr_version')

        if not incr_version:
            print 'Nothing to do.'
            return

        # Increments each field's data version
        updated = fields.update(data_version=F('data_version') + 1)

        print(u'{0} fields have been updated. Cached methods will '
              'lazily refresh their cache the next time they are '
              'accessed.'.format(updated))

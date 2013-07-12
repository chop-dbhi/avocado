import logging
from datetime import datetime
from django.db.models import F
from optparse import make_option
from avocado.management.base import DataFieldCommand

log = logging.getLogger(__name__)

_help = """\
Increments the `data_version` field on DataField instances to This will cause 
various cache that depends on this field to be refreshed the next time it is 
requested. To pre-cache, use the `avocado cache` command.
"""

class Command(DataFieldCommand):
    __doc__ = help = _help

    option_list = DataFieldCommand.option_list + (
        make_option('-m', '--modified', action='store_true',
            dest='update_data_version', default=False,
            help='Update `data_version` on `DataField` instances'),
    )

    def handle_fields(self, fields, **options):
        "Handles app_label or app_label.model_label formats."

        update_data_version = options.get('update_data_version')

        if not update_data_version:
            print 'Nothing to do.'
            return

        updated = fields.update(data_version=F('data_version')+1)

        print(u'{0} DataFields have been updated. Cached methods will '
            'lazily refresh their cache the next time they are '
            'accessed.'.format(updated))

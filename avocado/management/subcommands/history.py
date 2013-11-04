from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import transaction
from avocado.conf import settings
from avocado.history.models import Revision


class Command(BaseCommand):
    help = 'Utilities for managing the history API'

    option_list = BaseCommand.option_list + (
        make_option('--cull', action='store_true', help='Culls entries that '
                    'exceeds the maximum allowed history size for each '
                    'instance.'),

        make_option('--max-size', type=int, help='Specify the max history '
                    'size for commands that require it. Defaults to '
                    'HISTORY_MAX_SIZE.'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        cull = options.get('cull')
        max_size = options.get('max_size', settings.HISTORY_MAX_SIZE)

        if not cull:
            print('No option specified, nothing to do')
            return

        if not max_size:
            print('Unlimited history is allowed, nothing to do.')
            return

        # Get all distinct objects. Empty call to `order_by` removes the
        # ordering to save some overhead.
        objects = Revision.objects.values_list('object_id', 'content_type')\
            .order_by().distinct()

        # Prune history of each object
        for lookup in objects:
            Revision.objects.cull_for_object(*lookup, max_size=max_size)

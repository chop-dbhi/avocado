from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from avocado.conf import settings
from avocado.models import DataContext, DataView


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado history [options]

    DESCRIPTION:

        Utilities for managing the history API.

    OPTIONS:

        ``--prune`` - Prunes archived DataContext and DataView entries
        that exceeds HISTORY_MAX_SIZE.

    """

    help = 'Utilities for managing the history API'

    option_list = BaseCommand.option_list + (
        make_option('--prune', action='store_true',
            help='Prunes archived DataContext and DataView entries '
                'that exceeds HISTORY_MAX_SIZE'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        prune = options.get('prune')

        if not prune:
            print('No option specified, nothing to do')
            return

        if not settings.HISTORY_ENABLED:
            print('History not enabled, nothing to do.')
            return

        if not settings.HISTORY_MAX_SIZE:
            print('Unlimited history is allowed, nothing to do.')
            return

        # Base queryset of archived objects ordered by newest ones first
        views = DataView.objects.filter(archived=True).order_by('-modified')
        contexts = DataContext.objects.filter(archived=True).order_by('-modified')

        max_size = settings.HISTORY_MAX_SIZE

        # Note, this nested call is due to not being able to call delete()
        # when using a limit or offset, thus we must nest the query based on
        # primary key.
        delete = lambda x, y: x.objects.filter(pk__in=y).delete()

        # Prune archived objects from anonymous sessions
        delete(DataView, views.filter(user=None)[max_size:])
        delete(DataContext, contexts.filter(user=None)[max_size:])

        # Prune archived objects per user
        for user in User.objects.all():
            delete(DataView, views.filter(user=user)[max_size:])
            delete(DataContext, contexts.filter(user=user)[max_size:])

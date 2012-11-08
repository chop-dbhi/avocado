from optparse import make_option
from django.core.management.base import NoArgsCommand
from django.db import transaction
from avocado.models import DataField


class Command(NoArgsCommand):
    """
    SYNOPSIS::

        python manage.py avocado orphaned [options...]

    DESCRIPTION:

        Determines if any ``Fields`` are no longer valid. This is
        typically only necessary when a data model change occurs. An orphaned
        ``DataField`` will be marked if they are currently published
        (``[P]``).

    OPTIONS:

        ``--unpublish`` - unpublishes orphaned ``DataField`` if currently
        published

    """

    help = "Determines outdated or orphaned Fields."

    option_list = NoArgsCommand.option_list + (
        make_option('--unpublish', action='store_true',
            dest='unpublish', default=False,
            help='Unpublishes orphaned Fields'),
    )

    def _print(self, fields, msg, unpublish=False):
        print
        print '{0}:\n'.format(msg)
        for f in fields:
            print '\t',
            if f.published:
                if unpublish:
                    f.published = False
                    f.save()
                print '[P]',
            else:
                print '   ',
            print f
        print

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        unpublish = options.get('unpublish')
        verbosity = options.get('verbosity')

        unknown_models = []
        unknown_fields = []

        for f in DataField.objects.iterator():
            if f.model is None:
                unknown_models.append(f)
            elif f.field is None:
                unknown_fields.append(f)

        if verbosity:
            if not unknown_models and not unknown_fields:
                print '0 fields orphaned'
            else:
                print '\nKey:\n'
                print '\t[P] - field is published\n'
                if unknown_models:
                    self._print(unknown_models, 'The following Fields have an unknown model', unpublish)
                if unknown_fields:
                    self._print(unknown_fields, 'The following Fields have an unknown field', unpublish)

from optparse import make_option
from django.core.management.base import NoArgsCommand

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

    def _print(self, objs, msg, unpublish=False):
        print
        print '{}:\n'.format(msg)
        for o in objs:
            print '\t',
            if o.published:
                if unpublish:
                    o.published = False
                    o.save()
                print '[P]',
            else:
                print '   ',
            print o
        print

    def handle_noargs(self, **options):
        unpublish = options.get('unpublish')
        verbosity = options.get('verbosity')

        unknown_models = []
        unknown_fields = []

        for datafield in DataField.objects.iterator():
            if datafield.model is None:
                unknown_models.append(datafield)
            elif datafield.field is None:
                unknown_fields.append(datafield)

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

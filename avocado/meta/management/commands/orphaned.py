from optparse import make_option
from django.core.management.base import NoArgsCommand

from avocado.meta.models import Definition

class Command(NoArgsCommand):
    """
    SYNOPSIS::

        python manage.py avocado orphaned [options...]

    DESCRIPTION:

        Determines if any ``Definitions`` are no longer valid. This is
        typically only necessary when a data model change occurs. An orphaned
        ``Definition`` will be marked if they are currently published
        (``[P]``).

    OPTIONS:

        ``--unpublish`` - unpublishes orphaned ``Definition`` if currently
        published

    """

    help = "Determines outdated or orphaned Definitions."

    option_list = NoArgsCommand.option_list + (
        make_option('--unpublish', action='store_true',
            dest='unpublish', default=False,
            help='Unpublishes orphaned Definitions'),
    )

    def _print(self, objs, msg, unpublish=False):
        print
        print '%s:\n', msg
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

    def handle_noargs(self, **options):
        unpublish = options.get('unpublish')
        verbosity = options.get('verbosity')

        definitions = Definition.objects.all()

        unknown_models = []
        unknown_fields = []

        for d in definitions:
            if d.model is None:
                unknown_models.append(d)
            elif d.field is None:
                unknown_fields.append(d)

        if verbosity:
            if not unknown_models and not unknown_fields:
                print '0 definitions orphaned'
            else:
                if unknown_models:
                    self._print(unknown_models, 'The following Definitions have an unknown model', unpublish)
                if unknown_fields:
                    self._print(unknown_fields, 'The following Definitions have an unknown field', unpublish)

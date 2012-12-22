from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template import loader, Context
from django.conf import settings as django_settings
from avocado.models import DataField
from avocado.conf import OPTIONAL_DEPS
from modeltree.tree import trees


class Command(BaseCommand):
    help = """Performs a series of checks for the setup and installation as well
    as checks for any orphaned data fields.
    """

    __doc__ = help

    option_list = BaseCommand.option_list + (
        make_option('--output', default='stdout',
            help='Specify the output type: stdout, html'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        output = options.get('output')

        unknown_models = []
        unknown_fields = []


        for f in DataField.objects.iterator():
            if f.model is None:
                unknown_models.append(f)
            elif f.field is None:
                unknown_fields.append(f)

        # Ensure the default tree is valid
        try:
            trees.default
            default_modeltree = trees.modeltrees['default']['model']
        except Exception:
            default_modeltree = None

        context = {
            'unknown_models': unknown_models,
            'unknown_fields': unknown_fields,
            'optional_deps': OPTIONAL_DEPS,
            'settings': getattr(django_settings, 'AVOCADO', {}),
            'export_package_installed': 'avocado.export' in django_settings.INSTALLED_APPS,
            'default_modeltree': default_modeltree,
        }

        if output == 'stdout':
            template = loader.get_template('avocado/check.txt')
        elif output == 'html':
            template = loader.get_template('avocado/check.html')

        return template.render(Context(context))

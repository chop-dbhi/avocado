import sys
from optparse import make_option

from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.core.management.base import BaseCommand

from avocado.models import Criterion, Column

class Command(BaseCommand):
    help = "Generates a report of all the metadata that exists."

    option_list = BaseCommand.option_list + (
        make_option('-t', '--type', dest='mimetype', default='txt',
            help='Specifies which template type to use e.g. text or html'),
    )

    def handle(self, *args, **options):
        template_name = '.'.join(['avocado/doc', options['mimetype']])
        try:
            t = get_template(template_name)
        except TemplateDoesNotExist:
            sys.stderr.write('ERROR: No template exists for that type\n')
            sys.exit(1)

        criteria = Criterion.objects.public().order_by('order')
        columns = Column.objects.public().order_by('order')

        c = Context({
            'criteria': criteria,
            'columns': columns
        })

        output = t.render(c)

        sys.stdout.write(output)
        sys.exit(0)

import sys
import locale
import codecs
from optparse import make_option

from django.core.management.base import BaseCommand

from avocado import docs

class Command(BaseCommand):
    help = "Generates a report of all the metadata that exists."

    option_list = BaseCommand.option_list + (
        make_option('-t', '--type', dest='mimetype', default='txt',
            help='Specifies which template type to use e.g. text or html'),
    )

    def handle(self, *args, **options):
        output = docs.generate_fields_doc(mimetype=options['mimetype'])
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
        sys.stdout.write(output)
        sys.exit(0)

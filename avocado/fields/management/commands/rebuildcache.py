from django.core.management.base import NoArgsCommand
from mako.fields.cache import field_cache

class Command(NoArgsCommand):
    help = u'Flushes and rebuilds cache for public fields'

    def handle_noargs(self, **options):
        field_cache.rebuild_cache()

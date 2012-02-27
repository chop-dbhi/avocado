from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "A wrapper for Avocado subcommands"

    commands = ['sync', 'orphaned']
    command_prefix = 'avocado_%s'

    def handle(self, *args, **options):
        if not args or args[0] not in self.commands:
            return self.print_help('./manage.py', 'avocado')
        subcommand, args = args[0], args[1:]
        return call_command(self.command_prefix % subcommand, *args, **options)


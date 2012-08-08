import os
import sys
from django.test import TestCase
from django.core import management


class CommandsTestCase(TestCase):
    def test_subcommands(self):
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        management.call_command('avocado', 'sync', 'subcommands')
        management.call_command('avocado', 'cache', 'subcommands')
        management.call_command('avocado', 'orphaned')
        management.call_command('avocado', 'data', 'subcommands', update_data_modified=True)
        sys.stdout = stdout

import os
import sys
from django.core import management
from avocado.tests.base import BaseTestCase


class CommandsTestCase(BaseTestCase):
    def test_subcommands(self):
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        management.call_command('avocado', 'sync', 'tests')
        management.call_command('avocado', 'cache', 'tests')
        management.call_command('avocado', 'orphaned')
        management.call_command('avocado', 'data', 'tests', update_data_modified=True)
        sys.stdout = stdout

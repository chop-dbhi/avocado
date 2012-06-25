import os
import sys
from django.test import TestCase
from django.core import management

__all__ = ('BaseTestCase',)


class BaseTestCase(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        management.call_command('avocado', 'sync', 'tests')
        sys.stdout = stdout

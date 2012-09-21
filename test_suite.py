import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management
management.call_command('test', 'core', 'export', 'formatters', 'lexicon', 'models', 'query', 'sets', 'stats', 'subcommands')

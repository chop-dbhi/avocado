import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management
management.call_command('test', 'core', 'exporting', 'formatters',
    'lexicon', 'events', 'models', 'query', 'sets', 'stats', 'subcommands')

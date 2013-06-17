import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management

apps = [
    'test',
    'core',
    'exporting',
    'formatters',
    'lexicon',
    'events',
    'history',
    'models',
    'query',
    'sets',
    'stats',
    'search',
    'subcommands',
    'validation',
]

management.call_command(*apps)

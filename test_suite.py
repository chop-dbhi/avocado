import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management

apps = sys.argv[1:]

if not apps:
    apps = [
        'core',
        'exporting',
        'formatters',
        'events',
        'history',
        'models',
        'query',
        'stats',
        'search',
        'subcommands',
        'validation',
    ]

management.call_command('test', *apps)

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from django.core import management


apps = []

for arg in sys.argv[1:]:
    if arg == '--sqlite':
        os.environ['ENABLE_SQLITE'] = '1'
    elif arg == '--postgres':
        os.environ['ENABLE_POSTGRES'] = '1'
    elif arg == '--mysql':
        os.environ['ENABLE_MYSQL'] = '1'
    elif arg == '--no-sqlite':
        os.environ['ENABLE_SQLITE'] = '0'
    elif arg == '--no-postgres':
        os.environ['ENABLE_POSTGRES'] = '0'
    elif arg == '--no-mysql':
        os.environ['ENABLE_MYSQL'] = '0'
    elif arg.startswith('--default-engine'):
        engine = arg.split('=')[1]
        os.environ['DEFAULT_ENGINE'] = engine
    else:
        apps.append(arg)

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

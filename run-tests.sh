#!/bin/sh

ARGS="$@"

if [ ! $ARGS ]; then
    ARGS="avocado core exporting formatters lexicon models query sets stats subcommands"
fi

DJANGO_SETTINGS_MODULE='tests.settings' PYTHONPATH=. coverage run ../bin/django-admin.py test $ARGS
rm -rf docs/coverage
coverage html

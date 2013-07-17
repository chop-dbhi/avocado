#!/bin/sh

ARGS="$@"

if [ ! $ARGS ]; then
read -d '' ARGS <<- EOF
    avocado
    core
    exporting
    formatters
    lexicon
    events
    models
    query
    sets
    stats
    search
    subcommands
EOF
fi

DJANGO_SETTINGS_MODULE='tests.settings' PYTHONPATH=. coverage run `which django-admin.py` test $ARGS
rm -rf docs/coverage
coverage html

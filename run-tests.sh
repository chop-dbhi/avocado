#!/bin/sh

ARGS="$@"

if [ ! $ARGS ]; then
    ARGS="avocado lexicon"
fi

DJANGO_SETTINGS_MODULE='avocado.tests.settings' PYTHONPATH=. coverage run ../bin/django-admin.py test $ARGS
rm -rf docs/coverage
coverage html

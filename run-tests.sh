#!/bin/sh

DJANGO_SETTINGS_MODULE='avocado.tests.settings' PYTHONPATH=. coverage run ../bin/django-admin.py test $1
rm -rf docs/coverage
coverage html

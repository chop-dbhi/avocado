#!/bin/sh

DJANGO_SETTINGS_MODULE='avocado.tests.settings' PYTHONPATH=. coverage run ../bin/django-admin.py test avocado
rm -rf docs/coverage
coverage html

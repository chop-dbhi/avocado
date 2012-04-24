#!/bin/sh

DJANGO_SETTINGS_MODULE='avocado.tests.settings' PYTHONPATH=. ../bin/django-admin.py shell --verbosity=3

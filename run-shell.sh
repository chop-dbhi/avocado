#!/bin/sh

DJANGO_SETTINGS_MODULE='tests.settings' PYTHONPATH=. `which django-admin.py` shell --verbosity=3

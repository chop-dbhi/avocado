"""
A variety of signals that should be registered within the project that is
utilizing avocado.
"""

import os
import sys

from django.conf import settings
from django.db import connections, transaction

def update_objectset_count(instance, action, pk_set, **kwargs):
    "Signal that updates the ObjectSet instance's `count' attribute."
    obj_count = None

    if action == 'post_add':
        obj_count = instance.count + len(pk_set)
    elif action == 'post_remove':
        obj_count = instance.count - len(pk_set)
    elif action == 'post_clear':
        obj_count = 0

    if action in ('post_add', 'post_remove', 'post_clear'):
        instance.count = obj_count
        instance.save()

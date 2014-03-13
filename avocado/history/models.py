import jsonfield
from copy import deepcopy
from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .managers import RevisionManager
from .utils import get_object_data


class Revision(models.Model):
    # Generic foreign key to the object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    # The serialized data for this revision
    data = jsonfield.JSONField(null=True, blank=True)

    # The user that created the revision
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='+revision')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # The timestamp of the revision
    timestamp = models.DateTimeField(default=datetime.now, db_index=True)

    # This revision represents a deleted object
    deleted = models.BooleanField(default=False)

    # The changes from the previous revision
    changes = jsonfield.JSONField(null=True, blank=True)

    objects = RevisionManager()

    class Meta(object):
        app_label = 'avocado'
        ordering = ('-timestamp',)
        get_latest_by = 'timestamp'

    def __unicode__(self):
        return '{0} @ {1}'.format(self.content_object, self.timestamp)

    def apply(self, instance, commit=True):
        "Applies this revision to an instance."
        for key, value in self.data.items():
            setattr(instance, key, deepcopy(value))
        if commit:
            instance.save()
        return instance

    def diff(self, instance, fields=None, reverse=False):
        """
        Returns the diff between the revision and the instance, relative
        to the revision. Changed values will include the old and new values
        under the 'old_value' and 'new_value' keys respectively.

        If `reverse` is true, the diff will be relative to the instance.
        If `fields` is not defined, the revision data keys will be used.
        """
        diff = {}

        previous = self.data or {}

        if not fields:
            fields = previous.keys()

        current = get_object_data(instance, fields=fields)

        for key in fields:
            if current.get(key) != previous.get(key):
                if reverse:
                    old_value = current.get(key)
                    new_value = previous.get(key)
                else:
                    old_value = previous.get(key)
                    new_value = current.get(key)

                diff[key] = {
                    'old_value': old_value,
                    'new_value': new_value
                }

        return diff

import jsonfield
from datetime import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


class Log(models.Model):
    # Reference to an object if one is applicable
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey()

    # The event name. This must be unique for the event type to ensure
    # data can be aggregated for analysis
    event = models.CharField(max_length=200)

    # Extra data for the particular log entry. This must be JSON serializable.
    data = jsonfield.JSONField(null=True, blank=True)

    # The user and/or session that caused the event
    user = models.ForeignKey(User, null=True, blank=True, related_name='+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # The timestamp of the event
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta(object):
        app_label = 'avocado'

    def __unicode__(self):
        if self.content_type:
            label = '{0}:{1}'.format(self.content_type.model, self.event)
            if self.object_id:
                label = '{0} for {1}'.format(label, self.content_object)
            return label
        return self.event

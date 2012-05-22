from django.db import models
from django.contrib.auth.models import User
from avocado.models import DataField


class Distribution(models.Model):
    "Defines a distribution with N dimensions."
    dimensions = models.ManyToManyField(DataField, related_name='distributions+')
    series = models.NullBooleanField()
    nulls = models.NullBooleanField()

    user = models.ForeignKey(User, null=True, blank=True,
        related_name='distributions')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        app_label = 'avocado'
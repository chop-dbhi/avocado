import jsonfield
from django.db import models
from django.contrib.auth.models import User
from avocado.models import Base
from avocado.managers import PublishedManager

class BaseUser(Base):
    user = models.ForeignKey(User, null=True)


class DataContext(BaseUser):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.
    """
    json = jsonfield.JSONField(null=True, blank=True)

    objects = PublishedManager()


class DataView(BaseUser):
    """JSON object representing a means of rendering one or more data concepts
    together. At a minimum this must contain a list of data concepts that
    are required for the view. Other metadata may be stored by the client for
    downstream use.
    """
    json = jsonfield.JSONField(null=True, blank=True)

    objects = PublishedManager()


class DataContextView(BaseUser):
    """Connects a data context and view together as one unit. This enables
    report-like interfaces for persisting references to data.

    Note, the context and view cannot be _shared_ with any other contextview.
    This is to prevent potential silent updates between contextivew.
    """
    context = models.OneToOneField(DataContext, related_name='contextview')
    view = models.OneToOneField(DataView, related_name='contextview')

    objects = PublishedManager()

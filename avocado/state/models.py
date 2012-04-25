import jsonfield
from django.db import models
from django.contrib.auth.models import User
from avocado.core.models import Base
from avocado.managers import PublishedManager


class BaseUser(Base):
    user = models.ForeignKey(User, null=True, related_name='%(class)ss')
    session = models.BooleanField(default=False)

    class Meta(object):
        abstract = True
        app_label = 'avocado'


class DataContext(BaseUser):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True)
    count = models.IntegerField(null=True, db_column='_count')

    objects = PublishedManager()


class DataView(BaseUser):
    """JSON object representing a means of rendering one or more data concepts
    together. At a minimum this must contain a list of data concepts that
    are required for the view. Other metadata may be stored by the client for
    downstream use.

    This corresponds to the `SELECT` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True)

    objects = PublishedManager()


class DataContextView(BaseUser):
    """Connects a data context and view together as one unit. This provides
    a full query-like interface.

    Note, the context and view cannot be _shared_ with any other contextview.
    This is to prevent potential silent updates between contextview.
    """
    view = models.OneToOneField(DataView, related_name='contextview')
    context = models.OneToOneField(DataContext, related_name='contextview')
    count = models.IntegerField(null=True, db_column='_count')

    objects = PublishedManager()

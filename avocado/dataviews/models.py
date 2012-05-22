import jsonfield
from django.db import models
from django.contrib.auth.models import User
from avocado.core.models import Base
from avocado.managers import PublishedManager
from avocado.models import DataContext


class Query(Base):
    """A query-like interface for building queries using the Avocado metadata.

    This is defined by two components, the `context` which defines the
    conditions of the query and the `view` which defines what data is being
    selected.

    The `unique_count` is determined by executing the query relative to
    the `model` with just the `context` applied. The `count` is determined
    when the `view` is also applied to the query.
    """
    context = models.ForeignKey(DataContext, null=True, blank=True)
    view = jsonfield.JSONField(null=True, blank=True)

    user = models.ForeignKey(User, null=True, related_name='queries')
    session = models.BooleanField(default=False)

    # The counts are relative to the model
    model_label = models.CharField(max_length=100, null=True,
        help_text='The root model used when executing the query.')

    count = models.IntegerField(null=True, db_column='_count')

    objects = PublishedManager()

    class Meta(object):
        app_label = 'avocado'

    @property
    def model(self):
        "Returns this Query's root model class."
        app_name, model_name = self.model_label.split('.')
        return models.get_model(app_name, model_name)

    def get_queryset(self, apply_context=True, apply_view=True, tree=None):
        tree = tree or self.model
        queryset = self.context.get_queryset(tree=tree)
        # TODO Apply view
        return queryset

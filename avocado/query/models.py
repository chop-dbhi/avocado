import jsonfield
from django.db import models
from modeltree.tree import trees
from . import parsers


class AbstractDataContext(models.Model):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True, default=dict,
        validators=[parsers.datacontext.validate])
    composite = models.BooleanField(default=False)
    count = models.IntegerField(null=True, db_column='_count')

    class Meta(object):
        abstract = True

    def _combine(self, other, operator):
        if not isinstance(other, self.__class__):
            raise TypeError('Other object must be a DataContext instance')
        cxt = self.__class__(composite=True)
        cxt.user_id = self.user_id or other.user_id
        if self.json and other.json:
            cxt.json = {
                'type': operator,
                'children': [
                    {'id': self.pk, 'composite': True},
                    {'id': other.pk, 'composite': True}
                ]
            }
        elif self.json:
            cxt.json = {'id': self.pk, 'composite': True}
        elif other.json:
            cxt.json = {'id': other.pk, 'composite': True}
        return cxt

    def __and__(self, other):
        return self._combine(other, 'and')

    def __or__(self, other):
        return self._combine(other, 'or')

    @property
    def model(self):
        "The model this context represents with respect to the count."
        if self.count is not None:
            return trees.default.root_model

    @classmethod
    def validate(cls, attrs, **context):
        "Validate `attrs` as a context."
        parsers.datacontext.validate(attrs, **context)

    def parse(self, tree=None, **context):
        "Returns a parsed node for this context."
        return parsers.datacontext.parse(self.json, tree=tree, **context)

    def apply(self, queryset=None, tree=None, **context):
        "Applies this context to a QuerySet."
        if tree is None and queryset is not None:
            tree = queryset.model
        return self.parse(tree=tree, **context).apply(queryset=queryset)

    def language(self, tree=None, **context):
        return self.parse(tree=tree, **context).language


class AbstractDataView(models.Model):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `SELECT` and `ORDER BY` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True, default=dict,
        validators=[parsers.dataview.validate])
    count = models.IntegerField(null=True, db_column='_count')

    class Meta(object):
        abstract = True

    @classmethod
    def validate(cls, attrs, **context):
        "Validates `attrs` as a view."
        parsers.dataview.validate(attrs, **context)

    def parse(self, tree=None, **context):
        "Returns a parsed node for this view."
        return parsers.dataview.parse(self.json, tree=tree, **context)

    def apply(self, queryset=None, tree=None, include_pk=True, **context):
        "Applies this context to a QuerySet."
        if tree is None and queryset is not None:
            tree = queryset.model
        return self.parse(tree=tree, **context).apply(queryset=queryset,
            include_pk=include_pk)

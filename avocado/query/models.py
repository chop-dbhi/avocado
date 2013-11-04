import jsonfield
from django.db import models
from modeltree.tree import trees
from . import oldparsers as parsers


def _sql_string(queryset):
    sql, params = queryset.query.sql_with_params()
    return sql % tuple([repr(str(x)) for x in params])


class AbstractDataContext(models.Model):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True, default=dict,
                               validators=[parsers.datacontext.validate])
    count = models.IntegerField(null=True, db_column='_count')
    tree = models.CharField(max_length=100, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            if 'json' in kwargs:
                raise TypeError("{0}.__init__() got multiple values for "
                                "keyword argument 'json'"
                                .format(self.__class__.__name__))
            args = list(args)
            kwargs['json'] = args.pop(0)
        super(AbstractDataContext, self).__init__(*args, **kwargs)

    class Meta(object):
        abstract = True

    def _combine(self, other, operator):
        if not isinstance(other, self.__class__):
            raise TypeError('Other object must be a DataContext instance')
        cxt = self.__class__()
        cxt.user_id = self.user_id or other.user_id
        if self.json and other.json:
            cxt.json = {
                'type': operator,
                'children': [
                    {'composite': self.pk},
                    {'composite': other.pk}
                ]
            }
        elif self.json:
            cxt.json = {'composite': self.pk}
        elif other.json:
            cxt.json = {'composite': other.pk}
        return cxt

    def __and__(self, other):
        return self._combine(other, 'and')

    def __or__(self, other):
        return self._combine(other, 'or')

    @property
    def model(self):
        "The model this context represents with respect to the count."
        if self.tree in trees:
            return trees[self.tree].root_model
        return trees.default.root_model

    @classmethod
    def validate(cls, attrs, **context):
        "Validate `attrs` as a context."
        return parsers.datacontext.validate(attrs, **context)

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

    def sql(self, *args, **kwargs):
        """Returns the SQL query string representative of this context.

        This takes the same arguments as `apply()`.
        """
        return _sql_string(self.apply(*args, **kwargs))


class AbstractDataView(models.Model):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `SELECT` and `ORDER BY` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True, default=dict,
                               validators=[parsers.dataview.validate])

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            if 'json' in kwargs:
                raise TypeError("{0}.__init__() got multiple values for "
                                "keyword argument 'json'"
                                .format(self.__class__.__name__))
            args = list(args)
            kwargs['json'] = args.pop(0)
        super(AbstractDataView, self).__init__(*args, **kwargs)

    class Meta(object):
        abstract = True

    @classmethod
    def validate(cls, attrs, **context):
        "Validates `attrs` as a view."
        return parsers.dataview.validate(attrs, **context)

    def parse(self, tree=None, **context):
        "Returns a parsed node for this view."
        return parsers.dataview.parse(self.json, tree=tree, **context)

    def apply(self, queryset=None, tree=None, include_pk=True, **context):
        "Applies this context to a QuerySet."
        if tree is None and queryset is not None:
            tree = queryset.model
        return self.parse(tree=tree, **context) \
            .apply(queryset=queryset, include_pk=include_pk)

    def sql(self, *args, **kwargs):
        """Returns the SQL query string representative of this view.

        This takes the same arguments as `apply()`.
        """
        return _sql_string(self.apply(*args, **kwargs))


class AbstractDataQuery(models.Model):
    """
    JSON object representing a complete query.

    The query is constructed from a context(providing the 'WHERE' statements)
    and a view(providing the 'SELECT' and 'ORDER BY" statements). This
    corresponds to all the statements of the SQL query to dictate what info
    to retrieve, how to filter it, and the order to display it in.
    """
    context_json = jsonfield.JSONField(
        null=True, blank=True, default=dict,
        validators=[parsers.datacontext.validate])
    view_json = jsonfield.JSONField(
        null=True, blank=True, default=dict,
        validators=[parsers.dataview.validate])

    # The count when just the context is applied
    distinct_count = models.IntegerField(null=True)
    # The count when the context and the view is applied
    record_count = models.IntegerField(null=True)
    tree = models.CharField(max_length=100, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            if 'context_json' in kwargs:
                raise TypeError("{0}.__init__() got multiple values for "
                                "keyword argument 'context_json'"
                                .format(self.__class__.__name__))

            if 'view_json' in kwargs:
                raise TypeError("{0}.__init__() got multiple values for "
                                "keyword argument 'view_json'"
                                .format(self.__class__.__name__))

            kwargs['context_json'] = args[0].get('context', None)
            kwargs['view_json'] = args[0].get('view', None)

        super(AbstractDataQuery, self).__init__(*args, **kwargs)

    class Meta(object):
        abstract = True
        verbose_name_plural = 'data queries'

    @property
    def context(self):
        return AbstractDataContext(json=self.context_json)

    @property
    def view(self):
        return AbstractDataView(json=self.view_json)

    @property
    def json(self):
        return {
            'context': self.context_json,
            'view': self.view_json
        }

    @property
    def model(self):
        "The model this query represents with respect to the counts."
        if self.tree in trees:
            return trees[self.tree].root_model
        return trees.default.root_model

    @classmethod
    def validate(cls, attrs, **context):
        "Validates `attrs` as a query."
        return parsers.dataquery.validate(attrs, **context)

    def parse(self, tree=None, **context):
        "Returns a parsed node for this query."
        json = {
            'context': self.context_json,
            'view': self.view_json,
        }
        return parsers.dataquery.parse(json, tree=tree, **context)

    def apply(self, queryset=None, tree=None, distinct=True, include_pk=True,
              **context):
        "Applies this context to a QuerySet."
        if tree is None and queryset is not None:
            tree = queryset.model
        return self.parse(tree=tree, **context) \
            .apply(queryset=queryset, distinct=distinct, include_pk=include_pk)

    def sql(self, *args, **kwargs):
        """Returns the SQL query string representative of this query.

        This takes the same arguments as `apply()`.
        """
        return _sql_string(self.apply(*args, **kwargs))

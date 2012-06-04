from modeltree.tree import trees
from modeltree.query import ModelTreeQuerySet
from django.core.exceptions import ValidationError


def has_keys(obj, keys):
    "Check the required keys are present in `obj`"
    for key in keys:
        if key not in obj:
            return False
    return True


class Node(object):
    def __init__(self, fields=None, ordering=None, **context):
        self.field_ids = fields or []
        self.ordering = ordering or []
        self.tree = context.pop('tree', None)
        self.context = context

    def apply(self, queryset=None):
        tree = trees[self.tree]
        if queryset is None:
            queryset = tree.get_queryset()
        queryset = ModelTreeQuerySet(tree, query=queryset.query)
        if self.field_ids:
            queryset = queryset.select(*[f.field for f in self.fields])
        if self.ordering:
            queryset = queryset.order_by(*self.order_by)
        return queryset

    def raw(self, queryset=None):
        queryset = self.apply(queryset)
        return queryset.raw()

    @property
    def fields(self):
        from avocado.models import DataField
        return DataField.objects.filter(pk__in=self.field_ids)

    @property
    def order_by(self):
        from avocado.models import DataField
        tree = trees[self.tree]
        fields = {f.pk: f for f in DataField.objects.filter(pk__in=[x[0] \
                for x in self.ordering])}

        order_by = []
        for pk, direction in self.ordering:
            qstr = tree.query_string_for_field(fields[pk].field)
            if direction == 'desc':
                qstr = '-' + qstr
            order_by.append(qstr)
        return order_by


def validate(fields=None, ordering=None, **context):
    node = Node(fields, ordering, **context)
    if fields and len(node.fields) != len(fields):
        raise ValidationError('One or more fields do not exist')
    if ordering and len(node.order_by) != len(ordering):
        raise ValidationError('One or more fields do not exist')


def parse(fields=None, ordering=None, **context):
    return Node(fields, ordering, **context)

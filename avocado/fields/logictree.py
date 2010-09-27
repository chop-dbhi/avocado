"""
The LogicTree provides a means of parsing a raw JSON-compatible structure. The
grammar is as follows:

    NODE    ::= F_NODE | L_NODE

    F_NODE  ::= '{'
                    'id'        ::= INT
                    'operator'  ::= STRING
                    'value'     ::= STRING | NUMBER | BOOL | None
                '}'

    L_NODE  ::= '{'
                    'type'  ::= 'AND' | 'OR'
                    'children'  ::= '[' NODE{2,} ']'
                '}'

Two examples as follows:

    # single F_NODE
    {
        'id': 1,
        'operator': 'exact',
        'value': 30
    }

    # nested L_NODE structure
    {
        'type': 'OR',
        'children': [{
            'id': 1,
            'operator': 'exact',
            'value': 30
        }, {
            'id': 1,
            'operator': 'exact',
            'value': 45
        }]
    }
"""
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS
from avocado.models import Field

class Node(object):
    condition = None
    annotations = None

    def get_field_ids(self):
        return []

    def apply(self, queryset, *args, **kwargs):
        if self.annotations:
            queryset = queryset.values('pk').annotate(**self.annotations)
        if self.condition:
            queryset = queryset.filter(self.condition)
        return queryset


class Condition(Node):
    "Contains information for a single query condition."
    def __init__(self, context=None, using=DEFAULT_MODELTREE_ALIAS, **kwargs):
        self.context = context
        self.using = using
        self.id = kwargs['id']
        self.operator = kwargs['operator']
        self.value = kwargs['value']

    def _get_field(self):
        if not hasattr(self, '_field'):
            self._field = Field.objects.get(id=self.id)
        return self._field
    field = property(_get_field)

    def _translate(self):
        condition, annotations = self.field.translate(self.operator, self.value,
            using=self.using, **self.context)
        self._condition = condition
        self._annotations = annotations

    def _get_condition(self):
        if not hasattr(self, '_condition'):
            self._translate()
        return self._condition
    condition = property(_get_condition)

    def _get_annotations(self):
        if not hasattr(self, '_annotations'):
            self._translate()
        return self._annotations
    annotations = property(_get_annotations)

    def get_field_ids(self):
        return [self.id]


class LogicalOperator(Node):
    "Provides a logical relationship between it's children."
    def __init__(self, type, using=DEFAULT_MODELTREE_ALIAS):
        self.using = using
        self.type = type
        self.children = []

    def _combine(self, q1, q2):
        if self.type.upper() == 'OR':
            return q1 | q2
        return q1 & q2

    def _get_condition(self):
        if not hasattr(self, '_condition'):
            condition = None
            for node in self.children:
                if condition:
                    condition = self._combine(node.condition, condition)
                else:
                    condition = node.condition
            self._condition = condition
        return self._condition
    condition = property(_get_condition)

    def _get_annotations(self):
        if not hasattr(self, '_annotations'):
            self._annotations = {}
            for node in self.children:
                self._annotations.update(node.annotations)
        return self._annotations
    annotations = property(_get_annotations)

    def get_field_ids(self):
        ids = []
        for node in self.children:
            ids.extend(node.get_field_ids())
        return ids


def transform(rnode, pnode=None, using=DEFAULT_MODELTREE_ALIAS, **context):
    "Takes the raw data structure and converts it into the node tree."
    if not rnode:
        return Node()

    if rnode.has_key('children'):
        # ensure the logic makes sense
        if len(rnode['children']) < 2:
            raise TypeError, 'a logical operator must apply to 2 or more ' \
                'conditions'
        node = LogicalOperator(rnode['type'], using=using)
        for child in rnode['children']:
            transform(child, node, using=using, **context)
    else:
        node = Condition(context, using=using, **rnode)
    # top level node returns, i.e. no parent node
    if pnode is None:
        return node
    pnode.children.append(node)

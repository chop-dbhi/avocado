"""
The LogicTree provides a means of parsing a raw JSON-compatible structure. The
grammar is as follows:

    NODE    ::= F_NODE | L_NODE

    F_NODE  ::= '{'
                    'fid'       ::= INT
                    'cid'       ::= INT | None
                    'operator'  ::= STRING
                    'value'     ::= STRING | NUMBER | BOOL | None
                '}'

    L_NODE  ::= '{'
                    'operator'  ::= 'AND' | 'OR'
                    'children'  ::= '[' NODE{2,} ']'
                '}'

Two examples as follows:

    # single F_NODE
    {
        'fid': 1,
        'cid': None,
        'operator': 'exact',
        'value': 30
    }

    # nested NODE structure
    {
        'operator': 'OR',
        'children': [{
            'fid': 1,
            'cid': None,
            'operator': 'exact',
            'value': 30
        }, {
            'fid': 1,
            'cid': None,
            'operator': 'exact',
            'value': 45
        }]
    }
"""
from avocado.models import Field, Criterion

class Node(object):
    def apply(self, queryset):
        # check to make sure the queryset uses the same root model as the
        # modeltree
        if not self.modeltree.check(queryset):
            raise RuntimeError, 'models differ between queryset and modeltree'
        if self.annotations:
            queryset = queryset.values('pk').annotate(**self.annotations)
        return queryset.filter(self.condition)


class FieldNode(Node):
    "Contains information for a single query condition."
    def __init__(self, modeltree, context, fid, operator, value, cid=None):
        self.modeltree = modeltree
        self.context = context
        self.fid = fid
        self.cid = cid
        self.operator = operator
        self.value = value

    def _get_field(self):
        if not hasattr(self, '_field'):
            self._field = Field.objects.get(id=self.fid)
        return self._field
    field = property(_get_field)

    def _get_criterion(self):
        if not hasattr(self, '_criterion'):
            if self.cid is None:
                self._criterion = None
            else:
                self._criterion = Criterion.objects.get(id=self.cid)
        return self._criterion
    criterion = property(_get_criterion)

    def _translate(self):
        cond, ants = self.field.translate(self.modeltree, self.operator,
            self.value, **self.context)
        self._condition = cond
        self._annotations = ants

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


class LogicNode(Node):
    "Provides a logical relationship between it's children."
    def __init__(self, modeltree, operator):
        self.modeltree = modeltree
        self.operator = operator
        self.children = []

    def _combine(self, q1, q2):
        if self.operator.upper() == 'OR':
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

    def field_ids(self):
        "Returns a unique set of field ids used."
        ids = []
        for node in self.children:
            if isinstance(node, LogicNode):
                ids.extend(node.field_ids())
            else:
                ids.append(node.fid)
        return set(ids)


def transform(modeltree, rnode, pnode=None, **context):
    "Takes the raw data structure and converts it into the node tree."
    if rnode.has_key('children'):
        # ensure the logic makes sense
        if len(rnode['children']) < 2:
            raise RuntimeError, 'a logical operator must apply to 2 or more ' \
                'statements'
        node = LogicNode(modeltree, rnode['operator'])
        for child in rnode['children']:
            transform(modeltree, child, node, **context)
    else:
        node = FieldNode(modeltree, context, **rnode)
    # top level node returns, i.e. no parent node
    if pnode is None:
        return node
    pnode.children.append(node)

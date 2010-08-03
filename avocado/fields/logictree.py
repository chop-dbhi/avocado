from avocado.fields.cache import cache as fieldcache
from avocado.criteria.cache import cache as critcache

class ModelFieldNode(object):
    "Contains information for a single query condition."
    def __init__(self, modeltree, fid, operator, value, cid=None):
        self.modeltree = modeltree
        self.fid = fid
        self.cid = cid
        self.operator = operator
        self.value = value

    def _get_field(self):
        if not hasattr(self, '_field'):
            self._field = fieldcache.get(self.fid)
        return self._field
    field = property(_get_field)

    def _get_criterion(self):
        if not hasattr(self, '_criterion'):
            self._criterion = critcache.get(self.cid)
        return self._criterion
    criterion = property(_get_criterion)

    def _get_q(self):
        if not hasattr(self, '_q'):
            q, ant, agg = self.field.q(self.value, self.operator, self.modeltree)
        return self._q
    q = property(_get_q)


class LogicNode(object):
    "Provides a logical relationship between it's children."
    def __init__(self, operator, **kwargs):
        self.operator = operator
        self.children = []
        self._collapsed = None

    def _combine(self, q1, q2):
        if self.operator.upper() == 'OR':
            return q1 | q2
        return q1 & q2

    def _get_q(self):
        if not hasattr(self, '_q'):
            q = None
            for node in self.children:
                if q:
                    q = self._combine(node.q, q)
                else:
                    q = node.q
            self._q = q
        return self._q
    q = property(_get_q)


def transform(modeltree, raw_node, pnode=None):
    "Takes the raw data structure and converts it into the node tree."
    if raw_node.has_key('children'):
        node = LogicNode(raw_node['operator'])
        for child in raw_node['children']:
            transform(modeltree, child, node)
    else:
        node = ModelFieldNode(modeltree=modeltree, **raw_node)

    # top level node returns, i.e. no parent node
    if pnode is None:
        return node

    pnode.children.append(node)
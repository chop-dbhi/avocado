from avocado.fields.cache import cache
from avocado.modeltree import DEFAULT_MODELTREE

class LogicTree(object):
    def __init__(self, modeltree=DEFAULT_MODELTREE):
        self.modeltree = modeltree

    def _combine(self, op, q1, q2):
        if op == 'or':
            return q1 | q2
        return q1 & q2

    def _q(self, concept_id, operator, value):
        field = cache.get(concept_id)
        return field.q(value, operator, modeltree=self.modeltree)

    def collapse(self, nodes, bitop=None):
        cq = None

        # iterate over siblings. siblings relate based on `bitop'
        for node in nodes:
            ntype, operator = node['type'], node['operator']

            if ntype == 'logic':
                q = self.collapse(node['children'], operator)
            elif ntype == 'field':
                q = self._q(node['id'], operator, node['value'])

            if cq is None:
                cq = q
            else:
                cq = self._combine(bitop, cq, q)

        return cq

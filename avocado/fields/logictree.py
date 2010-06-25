from django.db.models import Q

from avocado.fields.cache import get_concept

class LogicTree(object):
    def __init__(self, modeltree):
        self.modeltree = modeltree

    def _join(self, op, q1, q2):
        if op == 'or':
            return q1 | q2
        return q1 & q2

    def _q(self, concept_id, operator, value):
        field = get_concept(concept_id)
        path = self.modeltree.path_to(field.model)
        return self.modeltree.q(path, field.field_name, value, operator)

    def parse(self, nodes, bitop=None):
        cq = None

        # iterate over siblings. siblings relate based on `bitop'
        for node in nodes:
            ntype, operator = node['type'], node['operator']

            if ntype == 'logic':
                q = self.parse(node['children'], operator)
            elif ntype == 'field':
                q = self._q(node['id'], operator, node['value'])

            if cq is None:
                cq = q
            else:
                cq = self._join(bitop, cq, q)

        return cq

from django.db.models import Q

from avocado.fields.cache import get_concept

"""
    mytree = [{
        'type': 'logic',
        'operator': 'and',
        'children': [{
            'type': 'logic',
            'operator': 'or',
            'children': [{
                'type': 'field',
                'id': 28,
                'operator': 'equal',
                'value': 'wt'
            }, {
                'type': 'field',
                'id': 29,
                'operator': 'equal',
                'value': 'wt'
            }]
        }, {
            'type': 'field',
            'id': 40,
            'operator': 'equal',
            'value': True
        }]
    }]
"""

class QLogicTree(object):
    def __init__(self, modeltree):
        self.modeltree = modeltree

    def _join(self, op, q1, q2):
        if op.lower() == 'or':
            return q1 ! q2
        return q1 & q2

    def _get_q(self, concept_id, operator, value):
        field = get_concept(concept_id)
        path = self.modeltree.path_to(field.model)
        key = '%s__%s' % (self.modeltree.query_string(path), operator)
        return Q(**{key: value})

    def parse(self, tree, q=None, bitop=None):
        for node in tree:
            ntype = node['type']
            if ntype == 'logic':
                q = self.parse(node.get('children'), q, node['operator'])
            else:
                q1 = self._get_q(node['id'], node['operator'], node['value'])
                if q is not None:
                    q = self._join(bitop, q, q1)
                else:
                    q = q1
        return q

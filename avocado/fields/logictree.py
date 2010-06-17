from django.db.models import Q

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

def _join(op, q1, q2):
    if op == 'and':
        return q1 & q2
    return q1 | q2

def parse(tree, q=None, bitop=None):
    for node in tree:
        ntype = node.get('type')
        if ntype == 'logic':
            q = parse(node.get('children'), q, node['operator'])
        elif ntype == 'field':
            q1 = Q(**{'some_field__' + node['operator']: node['value']})
            if q is not None:
                q = _join(bitop, q, q1)
            else:
                q = q1
    return q

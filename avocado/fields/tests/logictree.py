from django.test import TestCase
from django.db.models import Q
from django.core.cache import cache

from avocado.modeltree import ModelTree
from avocado.fields.logictree import LogicTree
from avocado.models import Column

class LogicTreeTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        self.logictree = LogicTree(ModelTree(Column))
        cache.clear()

    def test_single_field(self):
        nodes = [{
            'type': 'field',
            'id': 1,
            'operator': 'iexact',
            'value': 'foobar'
        }]

        q = self.logictree.parse(nodes)
        self.assertEqual(str(q), str(Q(name__iexact='foobar')))

    def test_single_conditions(self):
        nodes = [{
            'type': 'logic',
            'operator': 'and',
            'children': [{
                'type': 'field',
                'id': 1,
                'operator': 'icontains',
                'value': 'test'
            }, {
                'type': 'field',
                'id': 2,
                'operator': 'exact',
                'value': 'test2'
            }]
        }]

        q1 = self.logictree.parse(nodes)
        q2 = Q(name__icontains='test') & Q(keywords__exact='test2')
        self.assertEqual(str(q1), str(q2))

        nodes[0]['operator'] = 'or'

        q3 = self.logictree.parse(nodes)
        q4 = Q(name__icontains='test') | Q(keywords__exact='test2')
        self.assertEqual(str(q3), str(q4))

    def test_multi_level_condition(self):
        nodes = [{
            'type': 'logic',
            'operator': 'and',
            'children': [{
                'type': 'field',
                'id': 1,
                'operator': 'in',
                'value': ['one', 'two'],
            }, {
                'type': 'logic',
                'operator': 'or',
                'children': [{
                    'type': 'field',
                    'id': 3,
                    'operator': 'exact',
                    'value': 'foobar'
                }, {
                    'type': 'field',
                    'id': 3,
                    'operator': 'exact',
                    'value': 'barbaz'
                }]
            }]
        }]

        q1 = self.logictree.parse(nodes)
        q2 = Q(name__in=['one', 'two']) & (Q(fields__name__exact='foobar') | Q(fields__name__exact='barbaz'))
        self.assertEqual(str(q1), str(q2))

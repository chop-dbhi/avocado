from django.test import TestCase
from django.db.models import Q
from django.core.cache import cache

from avocado.fields.logictree import LogicTree

class LogicTreeTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        self.logictree = LogicTree()
        cache.clear()

    def test_single_field(self):
        raw_node = {
            'fid': 1,
            'cid': 1,
            'operator': 'iexact',
            'value': 'foobar'
        }

        q = self.logictree.transform(raw_node).q
        self.assertEqual(str(q), str(Q(name__iexact='foobar')))

    def test_single_conditions(self):
        raw_node = {
            'operator': 'and',
            'children': [{
                'fid': 1,
                'operator': 'icontains',
                'value': 'test'
            }, {
                'fid': 2,
                'operator': 'exact',
                'value': 'test2'
            }]
        }

        q1 = self.logictree.transform(raw_node).q
        q2 = Q(keywords__exact='test2') & Q(name__icontains='test')
        self.assertEqual(str(q1), str(q2))

        raw_node['operator'] = 'or'

        q3 = self.logictree.transform(raw_node).q
        q4= Q(keywords__exact='test2') | Q(name__icontains='test')
        self.assertEqual(str(q3), str(q4))

    def test_multi_level_condition(self):
        raw_node = {
            'operator': 'and',
            'children': [{
                'fid': 1,
                'operator': 'in',
                'value': ['one', 'two'],
            }, {
                'operator': 'or',
                'children': [{
                    'fid': 3,
                    'operator': 'exact',
                    'value': 'foobar'
                }, {
                    'fid': 3,
                    'operator': 'exact',
                    'value': 'barbaz'
                }]
            }]
        }

        q1 = self.logictree.transform(raw_node).q
        q2 = (Q(fields__name__exact='barbaz') | Q(fields__name__exact='foobar')) & Q(name__in=['one', 'two'])

        self.assertEqual(str(q1), str(q2))

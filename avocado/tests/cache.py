from django.test import TestCase
from django.core.cache import cache

from avocado.cache import querystore

__all__ = ('QueryStoreTestCase',)

class QueryStoreTestCase(TestCase):
    def setUp(self):
        cache.clear()
        
        self.args = [
            {'query': ({}, (), ()), 'data': [(0, 1), (100, 2), (400, 3)]},
            {'query': ({}, (1,), ()), 'data': [(0, 4), (100, 5)]},
            {'query': ({'foo': 'bar'}, (1,), ()), 'data': [(0, 6)]},
        ]
        
        for x in self.args:
            for i in x['data']:
                a = x['query'] + i
                querystore.set(*a)

    def test_simple_get(self):
        for x in self.args:
            for i in x['data']:
                a = x['query'] + (i[0],)
                self.assertEqual(querystore.get(*a), i[1])
    
    def test_sizes(self):
        for x in self.args:
            self.assertEqual(len(querystore.get_datakeys(*x['query'])), len(x['data']))

    def test_offsets(self):
        base_args = self.args[0]['query']
        # 0 - 50
        args = base_args + (0, 50)
        self.assertTrue(querystore.get(*args))
        # 25 - 125
        args = base_args + (25,)
        self.assertFalse(querystore.get(*args))
        # 25 - 75
        args = base_args + (25, 50)
        self.assertTrue(querystore.get(*args))
        # 25 - 35
        args = base_args + (25, 10)
        self.assertTrue(querystore.get(*args))
        # 150 - 300
        args = base_args + (150, 150)
        self.assertFalse(querystore.get(*args))
        # 0 - 100
        args = base_args + (0, 150)
        self.assertTrue(querystore.get(*args))        
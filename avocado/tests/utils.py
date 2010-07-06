from django.test import TestCase

from avocado.utils.paginator import BufferedPaginator
from avocado.utils.camel import camel

__all__ = ('BufferedPaginatorTestCase', 'CamelCaserTestCase')

class BufferedPaginatorTestCase(TestCase):
    def test_base(self):
        kwargs = {
            'count': 100,
            'offset': 0,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 9, 10],
            'per_page': 2
        }
        
        bp = BufferedPaginator(**kwargs)
        
        self.assertEqual(bp.num_pages, 50)
        self.assertEqual(bp.cached_page_indices(), (1, 6))
        self.assertEqual(bp.cached_pages(), 5)
        
        self.assertTrue(bp.page(2).in_cache())
        self.assertFalse(bp.page(6).in_cache())
    
    def test_offset(self):
        kwargs = {
            'count': 100,
            'offset': 40,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 9, 10],
            'per_page': 2
        }
        
        bp = BufferedPaginator(**kwargs)
        
        self.assertEqual(bp.num_pages, 50)
        self.assertEqual(bp.cached_page_indices(), (21, 26))
        self.assertEqual(bp.cached_pages(), 5)
        
        self.assertFalse(bp.page(20).in_cache())
        self.assertTrue(bp.page(21).in_cache())
        self.assertFalse(bp.page(26).in_cache())

    def test_partial(self):

        kwargs = {
            'count': 20,
            'offset': -20, # negative offset relative to count results to 0
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 9, 10],
            'per_page': 40
        }
        
        bp = BufferedPaginator(**kwargs)
        
        self.assertEqual(bp.num_pages, 1)
        self.assertEqual(bp.cached_page_indices(), (1, 2))
        self.assertEqual(bp.cached_pages(), 1)        
        
        p1 = bp.page(1)
        self.assertTrue(p1.in_cache())
        self.assertEqual((p1.start_index(), p1.end_index()), (1, 20))
        self.assertEqual(p1.object_list, kwargs['object_list'])

    def test_partial_offset(self):

        kwargs = {
            'count': 20,
            'offset': 40,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 9, 10],
            'per_page': 40
        }
        
        bp = BufferedPaginator(**kwargs)
        
        self.assertEqual(bp.num_pages, 1)
        self.assertEqual(bp.cached_page_indices(), (0, 0))
        self.assertEqual(bp.cached_pages(), 0)
        
        p1 = bp.page(1)
        self.assertFalse(p1.in_cache())
        self.assertEqual((p1.start_index(), p1.end_index()), (None, None))
        self.assertEqual(p1.object_list, [])


class CamelCaserTestCase(TestCase):
    def test_base(self):
        d1 = {
            'foo_bar': 1,
            '_hello_world': 2,
            'hello_world_': 3,
            '__start_dub': 4,
            'end_dub__': 5,
        }
        
        d2 = {
            'secondLevel': d1,
            'foo__bar__': 1,
        }


        d3 = {
            'top_Level__': d2
        }
        
        self.assertEqual(camel.camel_keys(d1), {'helloWorld_': 3,
            'fooBar': 1, 'endDub__': 5, '__startDub': 4, '_helloWorld': 2})
        self.assertEqual(camel.camel_keys(d2), {'fooBar__': 1,
            'secondLevel': {'helloWorld_': 3, 'fooBar': 1, 'endDub__': 5,
            '__startDub': 4, '_helloWorld': 2}})
        self.assertEqual(camel.camel_keys(d3), {'topLevel__': {'fooBar__': 1,
            'secondLevel': {'helloWorld_': 3, 'fooBar': 1, 'endDub__': 5,
            '__startDub': 4, '_helloWorld': 2}}})
from django.test import TestCase
from avocado.core.paginator import BufferedPaginator

class BufferedPaginatorTestCase(TestCase):
    def test_base(self):
        kwargs = {
            'count': 100,
            'offset': 0,
            'buf_size': 10,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
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
            'buf_size': 10,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'per_page': 2
        }

        bp = BufferedPaginator(**kwargs)

        self.assertEqual(bp.num_pages, 50)
        self.assertEqual(bp.cached_page_indices(), (21, 26))
        self.assertEqual(bp.cached_pages(), 5)

        self.assertFalse(bp.page(20).in_cache())
        self.assertTrue(bp.page(21).in_cache())
        self.assertFalse(bp.page(26).in_cache())

        # try as a negative offset
        kwargs['offset'] = -60

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
            'offset': 0,
            'buf_size': 10,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
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

        kwargs['offset'] = 10

        bp = BufferedPaginator(**kwargs)

        self.assertEqual(bp.num_pages, 1)
        self.assertEqual(bp.cached_page_indices(), (0, 0))
        self.assertEqual(bp.cached_pages(), 0)

    def test_overlap(self):
        kwargs = {
            'count': 100,
            'offset': 50,
            'buf_size': 10,
            'object_list': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'per_page': 2
        }

        bp = BufferedPaginator(**kwargs)

        # use paginator's buf_size
        self.assertEqual(bp.get_overlap(45), (True, (45, 5), (None, None)))
        self.assertEqual(bp.get_overlap(47), (True, (47, 3), (None, None)))
        self.assertEqual(bp.get_overlap(55), (True, (None, None), (61, 5)))
        self.assertEqual(bp.get_overlap(52), (True, (None, None), (61, 2)))
        self.assertEqual(bp.get_overlap(20), (False, (20, 10), (None, None)))
        self.assertEqual(bp.get_overlap(70), (False, (70, 10), (None, None)))

        # explicit buf_size
        self.assertEqual(bp.get_overlap(47, 14), (True, (47, 3), (61, 1)))
        self.assertEqual(bp.get_overlap(20, 100), (True, (20, 30), (61, 60)))
        self.assertEqual(bp.get_overlap(55, 12), (True, (None, None), (61, 7)))
        self.assertEqual(bp.get_overlap(20, 8), (False, (20, 8), (None, None)))
        self.assertEqual(bp.get_overlap(70, 3), (False, (70, 3), (None, None)))

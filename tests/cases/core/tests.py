import os
from django.core import management
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured
from avocado.core.loader import Registry, AlreadyRegistered
from avocado.core.paginator import BufferedPaginator

__all__ = ('RegistryTestCase', 'BufferedPaginatorTestCase')

class RegistryTestCase(TestCase):
    def setUp(self):
        class A(object): pass
        class B(object): pass
        self.A = A
        self.B = B
        self.r = Registry(register_instance=False)

    def test_register(self):
        self.r.register(self.B)
        self.r.register(self.A)
        self.assertEqual(self.r.choices, [('A', 'A'), ('B', 'B')])

    def test_unregister(self):
        self.r.register(self.A)
        self.assertEqual(self.r.choices, [('A', 'A')])
        self.r.unregister(self.A)
        self.assertEqual(self.r.choices, [])

    def test_already(self):
        self.r.register(self.A)
        self.assertRaises(AlreadyRegistered, self.r.register, self.A)

    def test_default(self):
        class C(object): pass
        C.default = True
        self.r.register(C)
        self.assertEqual(self.r['foo'], C)

        class D(object): pass
        D.default = True
        self.assertRaises(ImproperlyConfigured, self.r.register, D)


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


@override_settings(SOUTH_TESTS_MIGRATE=True)
class BackupTestCase(TransactionTestCase):
    def test_fixture_dir(self):
        from avocado.core import backup
        self.assertEqual(backup.get_fixture_dir(), os.path.join(os.path.dirname(__file__), 'fixtures'))

    def test_safe_load_tmp(self):
        from avocado.core import backup
        from avocado.models import DataField

        management.call_command('avocado', 'init', 'subcommands')
        self.assertEqual(DataField.objects.count(), 11)

        backup_path = backup.safe_load('0001_avocado_metadata')

        self.assertTrue(os.path.exists(backup_path))
        self.assertEqual(DataField.objects.count(), 3)
        os.remove(backup_path)

    def test_safe_load(self):
        from avocado.core import backup
        from avocado.models import DataField

        management.call_command('avocado', 'init', 'subcommands')
        self.assertEqual(DataField.objects.count(), 11)

        backup_path = backup.safe_load('0001_avocado_metadata',
            backup_path='backup.json')

        self.assertTrue(os.path.exists('backup.json'))
        self.assertEqual(DataField.objects.count(), 3)
        os.remove(backup_path)

    def test_fixture_filenames(self):
        from avocado.core import backup
        filenames = backup._fixture_filenames(backup.get_fixture_dir())
        self.assertEqual(filenames, ['0001_avocado_metadata.json'])

    def test_next_fixture_name(self):
        from avocado.core import backup
        from avocado.conf import settings
        filename = backup.next_fixture_name(settings.METADATA_FIXTURE_SUFFIX,
            backup.get_fixture_dir())
        self.assertEqual(filename, '0002_avocado_metadata')

    def test_migration_call(self):
        from avocado.core import backup
        management.call_command('avocado', 'migration')
        migration_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        self.assertTrue(os.path.exists(os.path.join(migration_dir, '0002_avocado_metadata_migration.py')))
        os.remove(os.path.join(migration_dir, '0002_avocado_metadata_migration.py'))
        os.remove(os.path.join(backup.get_fixture_dir(), '0002_avocado_metadata.json'))

    def test_migration(self):
        management.call_command('migrate', 'core')

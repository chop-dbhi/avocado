import time
from django.db import models
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from ..models import Foo


class CacheProxyTestCase(TestCase):
    class ComplexNumber(models.Model):
        def __init__(self):
            from avocado.core.cache.model import CacheProxy
            from avocado.core.cache import instance_cache_key

            self.id = 100

            self.cache_proxy = CacheProxy(func=self.as_string,
                version='get_version', timeout=2,
                key_func=instance_cache_key)
            self.cache_proxy.func_self = self

        def get_version(self, label=None):
            return 1

        def as_string(self, *args):
            return "2+3i"

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test(self):
        c = self.ComplexNumber()

        # Should not be cached available or cached initialization
        self.assertIsNone(c.cache_proxy.get())
        self.assertFalse(c.cache_proxy.cached())

        self.assertEqual(c.cache_proxy.get_or_set(), '2+3i')

        # Should be cached now
        self.assertTrue(c.cache_proxy.cached())
        self.assertEqual(c.cache_proxy.get(), '2+3i')

        time.sleep(2)

        # Make sure the value expired
        self.assertIsNone(c.cache_proxy.get())
        self.assertFalse(c.cache_proxy.cached())

    def test_cache_disabled(self):
        c = self.ComplexNumber()
        c.cache_proxy.func_self = None

        self.assertIsNone(c.cache_proxy.cache_key)
        self.assertIsNone(c.cache_proxy.get())
        self.assertIsNone(c.cache_proxy.get_or_set())
        self.assertIsNone(c.cache_proxy.flush())
        self.assertFalse(c.cache_proxy.cached())


class CacheManagerTestCase(TestCase):
    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test(self):
        self.assertEqual(Foo.objects.get_query_set().count(), 0)

        for i in range(10):
            f = Foo()
            f.save()

        self.assertEqual(Foo.objects.get_query_set().count(), 10)


class CachedMethodTestCase(TestCase):
    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test(self):
        f = Foo()
        f.save()

        # Not cached upon initialization
        self.assertFalse(f.callable_versioned.cached())
        self.assertFalse(f.default_versioned.cached())
        self.assertFalse(f.versioned.cached())
        self.assertFalse(f.unversioned.cached())

        self.assertEqual(f.default_versioned(), [4])
        self.assertEqual(f.callable_versioned(), [3])
        self.assertEqual(f.versioned(), [2])
        self.assertEqual(f.unversioned(), [1])

        self.assertTrue(f.default_versioned.cached())
        self.assertTrue(f.callable_versioned.cached())
        self.assertTrue(f.versioned.cached())
        self.assertTrue(f.unversioned.cached())

        # Time passes..
        time.sleep(2)

        # default_versioned was created using the default arguments so it should
        # never expire. All the rest had a timeout.
        self.assertTrue(f.default_versioned.cached())
        self.assertFalse(f.callable_versioned.cached())
        self.assertFalse(f.versioned.cached())
        self.assertFalse(f.unversioned.cached())

        self.assertEqual(f.callable_versioned(), [3])
        self.assertEqual(f.versioned(), [2])
        self.assertEqual(f.unversioned(), [1])

        self.assertTrue(f.callable_versioned.cached())
        self.assertTrue(f.versioned.cached())
        self.assertTrue(f.unversioned.cached())

        f.default_versioned.flush()
        f.callable_versioned.flush()
        f.versioned.flush()
        f.unversioned.flush()

        self.assertFalse(f.default_versioned.cached())
        self.assertFalse(f.callable_versioned.cached())
        self.assertFalse(f.versioned.cached())
        self.assertFalse(f.unversioned.cached())


class TestIssue136(TestCase):
    def setUp(self):
        self.f1 = Foo(value=1)
        self.f1.save()

        self.f2 = Foo(value=100)
        self.f2.save()

        self.f1.default_versioned.flush()
        self.f2.default_versioned.flush()

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=False)
    def test_control(self):
        self.assertEqual(self.f1.default_versioned(), [1])
        self.assertEqual(self.f2.default_versioned(), [100])

        self.assertFalse(self.f1.default_versioned.cached())
        self.assertFalse(self.f2.default_versioned.cached())

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_bug(self):
        self.assertEqual(self.f1.default_versioned(), [1])
        self.assertEqual(self.f2.default_versioned(), [100])

        self.assertTrue(self.f1.default_versioned.cached())
        self.assertTrue(self.f2.default_versioned.cached())

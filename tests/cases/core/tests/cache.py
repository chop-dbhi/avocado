import time
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings
from avocado.core.cache import CacheProxy, instance_cache_key
from ..models import Foo


class ComplexNumber(models.Model):
    def __init__(self):
        self.pk = 100

    def get_version(self, label=None):
        return 1

    def as_string(self, *args, **kwargs):
        return '2+3i'


class CacheProxyTestCase(TestCase):
    def setUp(self):
        self.cp = CacheProxy(ComplexNumber.as_string,
                             version='get_version',
                             timeout=2,
                             key_func=instance_cache_key)

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test(self):
        c = ComplexNumber()

        # Ensure this is flushed prior to testing
        self.cp.flush(c)

        # Should not be cached available or cached initialization
        self.assertIsNone(self.cp.get(c))
        self.assertFalse(self.cp.cached(c))

        self.assertEqual(self.cp.get_or_set(c), '2+3i')

        # Should be cached now
        self.assertTrue(self.cp.cached(c))
        self.assertEqual(self.cp.get(c), '2+3i')

        time.sleep(2)

        # Make sure the value expired
        self.assertIsNone(self.cp.get(c))
        self.assertFalse(self.cp.cached(c))

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_arguments(self):
        c = ComplexNumber()

        # Ensure this is flushed prior to testing
        args = [5]
        kwargs = {'foo': Foo.objects.all()}

        # Reset planned tests
        self.cp.flush(c, args, kwargs)

        # Should not be cached available or cached initialization
        self.assertIsNone(self.cp.get(c, args, kwargs))
        self.assertFalse(self.cp.cached(c, args, kwargs))

        # Fixed value
        self.assertEqual(self.cp.get_or_set(c, args, kwargs), '2+3i')

        # Should be cached now
        self.assertTrue(self.cp.cached(c, args, kwargs))
        self.assertEqual(self.cp.get(c, args, kwargs), '2+3i')

        time.sleep(2)

        # Make sure the value expired
        self.assertIsNone(self.cp.get(c, args, kwargs))
        self.assertFalse(self.cp.cached(c, args, kwargs))


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
        self.assertFalse(f.callable_versioned.cached(f))
        self.assertFalse(f.default_versioned.cached(f))
        self.assertFalse(f.versioned.cached(f))
        self.assertFalse(f.unversioned.cached(f))

        self.assertEqual(f.default_versioned(), [4])
        self.assertEqual(f.callable_versioned(), [3])
        self.assertEqual(f.versioned(), [2])
        self.assertEqual(f.unversioned(), [1])

        self.assertTrue(f.default_versioned.cached(f))
        self.assertTrue(f.callable_versioned.cached(f))
        self.assertTrue(f.versioned.cached(f))
        self.assertTrue(f.unversioned.cached(f))

        # Time passes..
        time.sleep(2)

        # default_versioned was created using the default arguments so
        # it should never expire. All the rest had a timeout.
        self.assertTrue(f.default_versioned.cached(f))
        self.assertFalse(f.callable_versioned.cached(f))
        self.assertFalse(f.versioned.cached(f))
        self.assertFalse(f.unversioned.cached(f))

        self.assertEqual(f.callable_versioned(), [3])
        self.assertEqual(f.versioned(), [2])
        self.assertEqual(f.unversioned(), [1])

        self.assertTrue(f.callable_versioned.cached(f))
        self.assertTrue(f.versioned.cached(f))
        self.assertTrue(f.unversioned.cached(f))

        f.default_versioned.flush(f)
        f.callable_versioned.flush(f)
        f.versioned.flush(f)
        f.unversioned.flush(f)

        self.assertFalse(f.default_versioned.cached(f))
        self.assertFalse(f.callable_versioned.cached(f))
        self.assertFalse(f.versioned.cached(f))
        self.assertFalse(f.unversioned.cached(f))


class TestIssue136(TestCase):
    def setUp(self):
        self.f1 = Foo(value=1)
        self.f1.save()

        self.f2 = Foo(value=100)
        self.f2.save()

        self.f1.default_versioned.flush(self.f1)
        self.f2.default_versioned.flush(self.f2)

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=False)
    def test_control(self):
        self.assertEqual(self.f1.default_versioned(), [1])
        self.assertEqual(self.f2.default_versioned(), [100])

        self.assertFalse(self.f1.default_versioned.cached(self.f1))
        self.assertFalse(self.f2.default_versioned.cached(self.f2))

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_bug(self):
        self.assertEqual(self.f1.default_versioned(), [1])
        self.assertEqual(self.f2.default_versioned(), [100])

        self.assertTrue(self.f1.default_versioned.cached(self.f1))
        self.assertTrue(self.f2.default_versioned.cached(self.f2))

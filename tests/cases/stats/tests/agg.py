import sys
import unittest
from django.test import TestCase
from django.test.utils import override_settings
from django.core import management
from django.db import DatabaseError
from avocado.models import DataField


class AggregatorTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)
        self.is_manager = DataField.objects\
            .get_by_natural_key('tests', 'employee', 'is_manager')
        self.salary = DataField.objects\
            .get_by_natural_key('tests', 'title', 'salary')
        self.first_name = DataField.objects\
            .get_by_natural_key('tests', 'employee', 'first_name')

    def test_count(self):
        self.assertEqual(self.is_manager.count(), [{'count': 6}])
        self.assertEqual(self.salary.count(), [{'count': 7}])
        self.assertEqual(self.first_name.count(), [{'count': 6}])

        queryset = self.is_manager.model.objects.filter(is_manager=True)
        self.assertEqual(
            self.is_manager.count(queryset=queryset), [{'count': 1}])

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_count_cached(self):
        self.is_manager.count.flush(self.is_manager)
        # After this, the count should now be cached
        self.assertEqual(self.is_manager.count(), [{'count': 6}])
        # Better be cached since we just looked it up
        self.assertTrue(self.is_manager.count.cached(self.is_manager))
        self.is_manager.count.flush(self.is_manager)
        # We just flushed the cache so it should not be cached anymore
        self.assertFalse(self.is_manager.count.cached(self.is_manager))

    def test_max(self):
        self.assertEqual(self.is_manager.max(), [{'max': 1}])
        self.assertEqual(self.salary.max(), [{'max': 200000}])
        self.assertEqual(self.first_name.max(), [{'max': 'Zac'}])

        queryset = self.salary.model.objects.filter(salary__lt=200000)
        self.assertEqual(self.salary.max(queryset=queryset), [{'max': 100000}])

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_max_cached(self):
        self.is_manager.max.flush(self.is_manager)
        # After this, the max should now be cached
        self.assertEqual(self.is_manager.max(), [{'max': 1}])
        # Better be cached since we just looked it up
        self.assertTrue(self.is_manager.max.cached(self.is_manager))
        self.is_manager.max.flush(self.is_manager)
        # We just flushed the cache so it should not be cached anymore
        self.assertFalse(self.is_manager.max.cached(self.is_manager))

    def test_min(self):
        self.assertEqual(self.is_manager.min(), [{'min': 0}])
        self.assertEqual(self.salary.min(), [{'min': 10000}])
        self.assertEqual(self.first_name.min(), [{'min': 'Aaron'}])

        queryset = self.salary.model.objects.filter(salary__gt=100000)
        self.assertEqual(self.salary.min(queryset=queryset), [{'min': 200000}])

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_min_cached(self):
        self.is_manager.min.flush(self.is_manager)
        # After this, the min should now be cached
        self.assertEqual(self.is_manager.min(), [{'min': 0}])
        # Better be cached since we just looked it up
        self.assertTrue(self.is_manager.min.cached(self.is_manager))
        self.is_manager.min.flush(self.is_manager)
        # We just flushed the cache so it should not be cached anymore
        self.assertFalse(self.is_manager.min.cached(self.is_manager))

    def test_avg(self):
        self.assertEqual(self.is_manager.avg(), None)
        self.assertEqual(self.salary.avg(), [{'avg': 53571.42857142857}])
        self.assertEqual(self.first_name.avg(), None)

        queryset = self.salary.model.objects.filter(salary__gte=100000)
        self.assertEqual(self.salary.avg(queryset=queryset), [{'avg': 150000}])

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_avg_cached(self):
        self.salary.avg.flush(self.salary)
        # After this, the avg should now be cached
        self.assertEqual(self.salary.avg(), [{'avg': 53571.42857142857}])
        # Better be cached since we just looked it up
        self.assertTrue(self.salary.avg.cached(self.salary))
        self.salary.avg.flush(self.salary)
        # We just flushed the cache so it should not be cached anymore
        self.assertFalse(self.salary.avg.cached(self.salary))

    def test_sum(self):
        self.assertEqual(self.is_manager.sum(), None)
        self.assertEqual(self.salary.sum(), [{'sum': 375000}])
        self.assertEqual(self.first_name.sum(), None)

        queryset = self.salary.model.objects.filter(salary__gte=100000)
        self.assertEqual(self.salary.sum(queryset=queryset), [{'sum': 300000}])

    @override_settings(AVOCADO_DATA_CACHE_ENABLED=True)
    def test_sum_cached(self):
        self.salary.sum.flush(self.salary)
        # After this, the sum should now be cached
        self.assertEqual(self.salary.sum(), [{'sum': 375000}])
        # Better be cached since we just looked it up
        self.assertTrue(self.salary.sum.cached(self.salary))
        self.salary.sum.flush(self.salary)
        # We just flushed the cache so it should not be cached anymore
        self.assertFalse(self.salary.sum.cached(self.salary))

    # Python unittest versions before 2.7 do not support expectedFailure so
    # check for raised exceptions explicitly in earlier versions.
    if sys.version_info >= (2, 7):
        @unittest.expectedFailure
        def test_stddev(self):
            self.assertEqual(self.is_manager.stddev(), None)
            self.assertEqual(self.salary.stddev(), [{'stddev': 66639.4502268}])
            self.assertEqual(self.first_name.stddev(), None)

            queryset = self.salary.model.objects.filter(salary__lt=20000)
            self.assertEqual(
                self.salary.stddev(queryset=queryset), [{'stddev': 2500}])
    else:
        def test_stddev(self):
            self.assertRaises(DatabaseError, self.is_manager.stddev())
            self.assertRaises(TypeError, self.salary.stddev())
            self.assertRaises(DatabaseError, self.first_name.stddev())

    if sys.version_info >= (2, 7):
        @unittest.expectedFailure
        def test_variance(self):
            self.assertEqual(self.is_manager.variance(), None)
            self.assertEqual(self.salary.variance(), [{
                'variance': 4440816326.530612
            }])
            self.assertEqual(self.first_name.variance(), None)

            queryset = self.salary.model.objects.filter(salary__lt=20000)
            self.assertEqual(self.salary.variance(queryset=queryset), [{
                'variance': 6250000
            }])
    else:
        def test_variance(self):
            self.assertRaises(DatabaseError, self.is_manager.variance())
            self.assertRaises(TypeError, self.salary.variance())
            self.assertRaises(DatabaseError, self.first_name.variance())

import sys
import unittest
from django.test import TestCase
from django.core import management
from django.db import DatabaseError
from avocado.models import DataField


class AggregatorTestCase(TestCase):
    fixtures = ['stats.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'stats', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('stats', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('stats', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key('stats', 'employee', 'first_name')

    def test_count(self):
        self.assertEqual(self.is_manager.count(), [{'count': 6}])
        self.assertEqual(self.salary.count(), [{'count': 7}])
        self.assertEqual(self.first_name.count(), [{'count': 6}])

    def test_max(self):
        self.assertEqual(self.is_manager.max(), [{'max': 1}])
        self.assertEqual(self.salary.max(), [{'max': 200000}])
        self.assertEqual(self.first_name.max(), [{'max': 'Zac'}])

    def test_min(self):
        self.assertEqual(self.is_manager.min(), [{'min': 0}])
        self.assertEqual(self.salary.min(), [{'min': 10000}])
        self.assertEqual(self.first_name.min(), [{'min': 'Aaron'}])

    def test_avg(self):
        self.assertEqual(self.is_manager.avg(), None)
        self.assertEqual(self.salary.avg(), [{'avg': 53571.42857142857}])
        self.assertEqual(self.first_name.avg(), None)

    def test_sum(self):
        self.assertEqual(self.is_manager.sum(), None)
        self.assertEqual(self.salary.sum(), [{'sum': 375000}])
        self.assertEqual(self.first_name.sum(), None)

    # Python unittest versions before 2.7 do not support expectedFailure so 
    # check for raised exceptions explicitly in earlier versions.
    if sys.hexversion >= 0x02070000: 
        @unittest.expectedFailure
        def test_stddev(self):
            self.assertEqual(self.is_manager.stddev(), None)
            self.assertEqual(self.salary.stddev(), [{'stddev': 66639.4502268}])
            self.assertEqual(self.first_name.stddev(), None)
    else:
        def test_stddev(self):
            self.assertRaises(DatabaseError, self.is_manager.stddev())
            self.assertRaises(TypeError, self.salary.stddev())
            self.assertRaises(DatabaseError, self.first_name.stddev())

    if sys.hexversion >= 0x02070000: 
        @unittest.expectedFailure
        def test_variance(self):
            self.assertEqual(self.is_manager.variance(), None)
            self.assertEqual(self.salary.variance(), [{'variance': 4440816326.530612}])
            self.assertEqual(self.first_name.variance(), None)
    else:
        def test_variance(self):
            self.assertRaises(DatabaseError, self.is_manager.variance())
            self.assertRaises(TypeError, self.salary.variance())
            self.assertRaises(DatabaseError, self.first_name.variance())

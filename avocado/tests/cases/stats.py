import unittest
from avocado.tests.base import BaseTestCase


class AggregatorTestCase(BaseTestCase):
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
        self.assertEqual(self.is_manager.avg(), [{'avg': 0.16666666666666666}])
        self.assertEqual(self.salary.avg(), [{'avg': 53571.42857142857}])
        self.assertEqual(self.first_name.avg(), [{'avg': 0.0}])

    def test_sum(self):
        self.assertEqual(self.is_manager.sum(), None)
        self.assertEqual(self.salary.sum(), [{'sum': 375000}])
        self.assertEqual(self.first_name.sum(), None)

    @unittest.expectedFailure
    def test_stddev(self):
        self.assertEqual(self.is_manager.stddev(), None)
        self.assertEqual(self.salary.stddev(), [{'stddev': 66639.4502268}])
        self.assertEqual(self.first_name.stddev(), None)

    @unittest.expectedFailure
    def test_variance(self):
        self.assertEqual(self.is_manager.variance(), None)
        self.assertEqual(self.salary.variance(), [{'variance': 4440816326.530612}])
        self.assertEqual(self.first_name.variance(), None)

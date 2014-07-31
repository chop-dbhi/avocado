import sys
import pstats
import cProfile
import unittest
from django.test.simple import DjangoTestSuiteRunner


class ProfilingTestRunner(DjangoTestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        stream = open('profiled_tests.txt', 'w')

        # failfast keyword was added in Python 2.7 so we need to leave it out
        # when creating the runner if we are running an older python version.
        if sys.version_info >= (2, 7):
            runner = unittest.TextTestRunner(
                verbosity=self.verbosity, failfast=self.failfast).run
        else:
            runner = unittest.TextTestRunner(verbosity=self.verbosity).run

        profile = cProfile.Profile()
        profile.runctx('result = run_tests(suite)', {
            'run_tests': runner,
            'suite': suite,
        }, locals())
        profile.create_stats()
        stats = pstats.Stats(profile, stream=stream)

        stats.sort_stats('time')
        stats.print_stats()
        return locals()['result']

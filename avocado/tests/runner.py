import pstats
import cProfile
import unittest
from django.test.simple import DjangoTestSuiteRunner


class ProfilingTestRunner(DjangoTestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        stream = open('profiled_tests.txt', 'w')

        runner = unittest.TextTestRunner(verbosity=self.verbosity, failfast=self.failfast).run

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

import sys
import cProfile
import unittest
from django.test.runner import DiscoverRunner


class ProfilingTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        kwargs['pattern'] = "**/*.py"
        super(ProfilingTestRunner, self).__init__(*args, **kwargs)

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

        profile.dump_stats('profiled_tests.txt')

        return locals()['result']

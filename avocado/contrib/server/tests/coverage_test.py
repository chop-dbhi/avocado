import os
import coverage
import colorize

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

class CoverageTestRunner(DjangoTestSuiteRunner):

    def run_tests(self, test_labels, verbosity=1, interactive=True, extra_tests=[]):
        coveragemodules = getattr(settings, 'COVERAGE_MODULES', [])

        if coveragemodules:
            coverage.start()

        self.setup_test_environment()

        suite = self.build_suite(test_labels, extra_tests)
        old_config = self.setup_databases()
        result = self.run_suite(suite)

        if coveragemodules:
            coverage.stop()
            coveragedir = getattr(settings, 'COVERAGE_DIR', './build/coverage')
            if not os.path.exists(coveragedir):
                os.makedirs(coveragedir)

            modules = []
            for module_string in coveragemodules:
                module = __import__(module_string, globals(), locals(), [""])
                modules.append(module)
                f,s,m,mf = coverage.analysis(module)
                fp = file(os.path.join(coveragedir, module_string + ".html"), "wb")
                colorize.colorize_file(f, outstream=fp, not_covered=mf)
                fp.close()
            coverage.report(modules, show_missing=0)
            coverage.erase()

        self.teardown_databases(old_config)
        self.teardown_test_environment()

        return len(result.failures) + len(result.errors)

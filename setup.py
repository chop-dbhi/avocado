import sys
from setuptools import setup, find_packages
from setuptools.command import install as _install

if sys.version_info < (2, 7):
    sys.stdout.write('Python versions < 2.7 are not supported\n')
    sys.exit(1)


class install(_install.install):
    def run(self):
        _install.install.run(self)
        sys.stdout.write('NOTE: For `clustering` support, NumPy must '\
            'installed first, followed by SciPy.\n')

kwargs = {
    'cmdclass': {'install': install},

    # Packages
    'packages': find_packages(),
    'include_package_data': True,

    # Dependencies
    'install_requires': [
        'django>=1.4',
        'modeltree',
        'jsonfield>=0.9',
    ],

    'test_suite': 'test_suite',

    # Test dependencies
    'tests_require': [
        'django-guardian',
        'django-haystack>=2.0b',
        'whoosh',
        'openpyxl',
        'scipy',
        'numpy',
        'coverage',
        'python-memcached',
    ],

    # Optional dependencies
    'extras_require': {
        # Granular permission
        'permissions': ['django-guardian'],
        # Search
        'search': ['django-haystack>=2.0b'],
        # Clustering components.. unforunately SciPy must be installed separately
        # since NumPy is a dependency
        'clustering': ['numpy'],
        # Includes extra exporter dependencies
        'extras': ['openpyxl'],
    },

    # Resources unavailable on PyPi
    'dependency_links': [
        'https://github.com/toastdriven/django-haystack/tarball/master#egg=django-haystack-2.0',
    ],

    # Metadata
    'name': 'avocado',
    'version': __import__('avocado').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Metadata APIs for Django',
    'license': 'BSD',
    'keywords': 'query metadata',
    'url': 'https://github.com/cbmi/avocado/',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7'
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
    ],
}

setup(**kwargs)

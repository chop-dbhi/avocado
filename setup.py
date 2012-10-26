import sys
from setuptools import setup, find_packages
from setuptools.command import install as _install


class install(_install.install):
    def run(self):
        _install.install.run(self)
        sys.stdout.write('NOTE: For `clustering` support, NumPy must '\
            'installed first, followed by SciPy.\n')

kwargs = {
    'cmdclass': {'install': install},

    # Packages
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    'include_package_data': True,

    # Dependencies
    'install_requires': [
        'django>=1.4,<1.5',
        'modeltree==1.1',

        # Uses a dependency link below
        'jsonfield>=1.0b',
    ],

    'test_suite': 'test_suite',

    # Test dependencies
    'tests_require': [
        'django-guardian',
        'django-haystack',
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
        'search': ['django-haystack'],
        # Clustering components.. unforunately SciPy must be installed
        # separately since NumPy is a dependency
        'clustering': ['numpy'],
        # Includes extra exporter dependencies
        'extras': ['openpyxl'],
    },

    'dependency_links': [
        'https://github.com/cbmi/django-jsonfield/zipball/601872f#egg=jsonfield-1.0b',
    ],

    # Metadata
    'name': 'avocado',
    'version': __import__('avocado').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Metadata APIs for Django',
    'license': 'BSD',
    'keywords': 'query metadata harvest orm',
    'url': 'http://cbmi.github.com/avocado/',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
    ],
}

setup(**kwargs)

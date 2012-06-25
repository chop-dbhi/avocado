import sys
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

if sys.version_info < (2, 7):
    sys.stdout.write('Python versions < 2.7 are not supported\n')
    sys.exit(1)

kwargs = {
    # Packages
    'packages': find_packages(),
    'include_package_data': True,

    # Dependencies
    'install_requires': [
        'django>=1.4',
        'modeltree',
        'django-jsonfield>=0.9',
    ],

    # Test dependencies
    'tests_require': [
        'django-guardian',
        'django-haystack>=2.0',
        'whoosh',
        'openpyxl',
        'scipy',
        'numpy',
        'coverage',
    ],

    # Optional dependencies
    'extras_require': {
        'django-guardian': [],
        'django-haystack': [],
        'openpyxl': [],
        'scipy': ['numpy'],
    },

    # Resources unavailable on PyPi
    'dependency_links': [
        'https://github.com/bradjasper/django-jsonfield/tarball/master#egg=django-jsonfield-0.9',
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

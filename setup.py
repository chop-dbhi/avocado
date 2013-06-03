import sys
from setuptools import setup, find_packages


install_requires = [
    'django>=1.4,<1.6',
    'modeltree>=1.1.5',
    'South==0.8.1',
    'jsonfield==0.9.4',
]

if sys.version_info < (2, 7):
    install_requires.append('ordereddict>=1.1')


kwargs = {
    # Packages
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    'include_package_data': True,

    # Dependencies
    'install_requires': install_requires,

    'test_suite': 'test_suite',

    # Test dependencies
    'tests_require': [
        'django-guardian==1.0.4',
        'django-haystack==1.2.7',
        'whoosh==2.4.1',
        'openpyxl>=1.6,<1.7',
        'python-memcached==1.48',
        'coverage',
    ],

    # Optional dependencies
    'extras_require': {
        # Granular permission
        'permissions': ['django-guardian==1.0.4'],
        # Search
        'search': ['django-haystack==1.2.7'],
        # Includes extra exporter dependencies
        'extras': ['openpyxl>=1.6,<1.7'],
    },

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
        'Programming Language :: Python :: 2.6',
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

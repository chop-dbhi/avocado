import sys
from setuptools import setup, find_packages


install_requires = [
    'django>=1.5,<1.7',
    'modeltree>=1.1.9',
    'South==1.0.2',
    'jsonfield==1.0.0',
    'django_rq',
]

if sys.version_info < (2, 7):
    install_requires.append('ordereddict>=1.1')


kwargs = {
    # Packages
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*',
                                       'tests.*']),
    'include_package_data': True,

    # Dependencies
    'install_requires': install_requires,

    'test_suite': 'test_suite',

    # Optional dependencies
    'extras_require': {
        # Granular permission
        'permissions': ['django-guardian>=1.1.0'],
        # Search
        'search': ['django-haystack>=2.1.0,<2.4'],
        # Includes extra exporter dependencies
        'extras': ['openpyxl>=1.7,<2.2'],
        # Pretty printing of SQL in the admin and for debugging
        'sql': ['sqlparse'],
    },

    # Metadata
    'name': 'avocado',
    'version': __import__('avocado').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Metadata APIs for Django',
    'license': 'BSD',
    'keywords': 'query metadata harvest orm',
    'url': 'http://github.com/cbmi/avocado',
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

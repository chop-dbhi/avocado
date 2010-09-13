from setuptools import setup, find_packages

kwargs = {
    'name': 'django-avocado',
    'version': '1.0',
    'author': 'Byron Ruth',
    'author_email': 'ruthb@email.chop.edu',
    'description': 'A data-driven query engine',
    'license': 'BSD',
    'keywords': 'snippets tools utilities',
    'install_requires': ['django>=1.2', 'django-compressor'],
    'package_data': {

    },
    'packages': find_packages(exclude=('*.tests', '*.tests.*')),
    'package_data': {
        'avocado': ['sql/*.sql']
    },
    'exclude_package_data': {
        '': ['fixtures/*']
    },
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
}

setup(**kwargs)

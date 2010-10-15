from setuptools import setup, find_packages

kwargs = {
    'name': 'django-avocado',
    'version': '1.0',
    'author': 'Byron Ruth',
    'author_email': 'ruthb@email.chop.edu',
    'description': 'A data-driven query engine',
    'license': 'BSD',
    'keywords': 'snippets tools utilities',

    'packages': find_packages(exclude=('*.tests', '*.tests.*')),

    'package_dir': {
        'avocado': 'avocado',
        'client': 'avocado/contrib/client',
        'server': 'avocado/contrib/server',
    }

    'package_data': {
        'avocado': ['sql/*.sql'],

        'client': [
            'static/js/src/*',
            'static/js/src/lib/*',
            'static/js/src/rest/*',
            'static/js/src/define/*',
            'static/js/src/report/*',

            'static/js/min/*',
            'static/js/min/lib/*',
            'static/js/min/rest/*',
            'static/js/min/define/*',
            'static/js/min/report/*',

            'templates/*'
        ]
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

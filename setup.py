from setuptools import setup, find_packages

setup(
    name = 'django-avocado',
    version = '1.0',
    author = 'Byron Ruth',
    author_email = 'ruthb@email.chop.edu',
    description = 'A data-driven query engine',
    license = 'BSD',
    keywords = 'snippets tools utilities',
    packages = find_packages(exclude=('tests',)),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

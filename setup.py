from setuptools import setup, find_packages

setup(
    name = 'django-avocado',
    version = '1.0',
    author = 'Byron Ruth',
    author_email = 'bruth@codeomics.com',
    description = 'A data-driven querying engine',
    license = 'BSD',
    keywords = 'snippets tools utilities',
    packages = find_packages(),
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

AVOCADO SETUP GUIDE
===================

Environment
-----------

If not starting a project from scratch and the environment and project
are already set up, skip to Packages_.

This is more of a general *good practices* guide for setting up a python
environment than being specific to Avocado. The prerequisites include:

    - setuptools_
    - virtualenv_
    - pip_

Once the above packages are installed, create the virtual environment::

    $ virtualenv --no-site-packages myenv

where ``myenv`` is a name for the new python environment. The
``--no-site-packages`` flag was added to prevent any version clashes between
system-wide installed python packages and local packages.

Once created, activate the environment by doing::

    $ cd myenv
    $ source bin/activate

This command ensures the local environment takes precedence for any interaction
with Python (go to the virtualenv_ website for more info). You can confirm the
environemnt is active by doing::

    $ which python

This should return the absolute path to ``python`` located in your environemnt.
Such as::

    $ which python
    /home/byron/myenv/bin/python

Packages
--------

The only dependency of Avocado is Django_ since it heavily relies on the ORM
(and thus the database backend) for it's API. Additional dependencies will be
noted as the guide proceeds when configuring certain settings. Simply do::

    $ pip install django-avocado

Pre-``syncdb``
--------------

Before running ``syncdb`` there are few settings that need to be discussed,
since they extend the base models defined in Avocado.

The first are called **Formatters**. Very simply, a formatter is a function
that takes *n* arguments and returns *m* values. For example, a concatenation
formatter may look like this::

    def concat(*args):
        return ' '.join([str(x) for x in args if x is not None])

Formatters can be used in different contexts depending on the arguments being
supplied. Ultimately the formatting is being performed to render a particular
representation for the client.For example, a ``full_name`` formatter may look
like this for an HTML representation::

    def html_full_name(first_name, last_name):
        return '%s %s' % (first_name, last_name)

while a comma-separated value (CSV) formatter may look like this::

    def csv_full_name(first_name, last_name):
        return [first_name, last_name]

Now why were the ``first_name`` and ``last_name`` simply returned in a list?
Well it is common for CSV representations to be in more of a raw data format.
If the CSV was exported and loaded into a spreadsheet, having separate columns
for the ``first_name`` and ``last_name`` would be necessary for proper sorting
operations.

For this reason, a list of formatter *types* can be specified as a setting::

    FORMATTER_TYPES = {
        'html': {
            'error': '<span style="color:red">Data Error</span>',
            'null': '<span style="color:grey">(No Data)</span>',
        },
        'csv': {
            'error': '[data error]',
            'null': '',
        }
    }
            
The keys of ``FORMATTER_TYPES`` represents the names of the formatter types.
Two default values can be set for when errors occur while formatting and for
null values (``None`` is Python).



.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _pip: http://pypi.python.org/pypi/pip
.. _Django: http://www.djangoproject.com

 

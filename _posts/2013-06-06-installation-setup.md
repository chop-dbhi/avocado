---
layout: page
title: "Installation & Setup"
category: doc
date: 2013-06-06 21:26:44
order: 1
---

## Prerequisites

To install Avocado and it's dependencies, it is assumed you have the latest versions of [distribute](http://pypi.python.org/pypi/distribute) (or [setuptools](http://pypi.python.org/pypi/setuptools)) and [Pip](http://pypi.python.org/pypi/pip) installed.

## Install

```
pip install avocado
```

The _hard_ dependencies which will auto-install include:

- [Django 1.4+](https://www.djangoproject.com)
- [modeltree 1.1+](http://pypi.python.org/pypi/modeltree)
- [django-jsonfield 0.9+](https://github.com/bradjasper/django-jsonfield/)
- [South 0.7.6+](http://south.readthedocs.org)

## Optional Dependencies

For a bare-bones Avocado installation the following dependencies may be skipped, but peruse through to understand the purpose of each one listed.

_Have a suggestion for additional metadata integration? [File an issue](https://github.com/cbmi/avocado/issues/new) on Avocado's GitHub repo._

#### [Django "sites" Framework](https://docs.djangoproject.com/en/1.4/ref/contrib/sites/)

Having this installed enables associating `DataField`s and/or `DataConcept`s to specific sites, or more specifically, deployments. For example, an internal and external deployment may exist for the same application, but only the internal deployment provides access to certain _restricted_ fields for operational use.

Install by adding `django.contrib.sites` to `INSTALLED_APPS`.

#### [django-guardian](http://packages.python.org/django-guardian/)

This enables fine-grain control over who has permissions for various `DataField`s. Permissions can be defined at a user or group level.

Install by doing `pip install django-guardian` and adding `guardian` to `INSTALLED_APPS`.

#### [django-haystack](http://haystacksearch.org)

What's having all this great descriptive data if no one can find it? Haystack provides search engine facilities for the metadata.

Install by doing `pip install django-haystack` and installing one of the supported search engine backends. The easiest to setup is [Whoosh](http://pypi.python.org/pypi/Whoosh) which is implemented in pure Python. Install it by doing `pip install whoosh`, then update your settings file with the following:

```python
# Add haystack
INSTALLED_APPS = (
    ...
    'haystack',
)

# Specify Haystack's siteconf module. This is generally project-specific,
# but Avocado provides one to get started.
HAYSTACK_SITECONF = 'avocado.search_sites'

# Specify the engine
HAYSTACK_SEARCH_ENGINE = 'whoosh'

# Add engine-specific config. Whoosh uses a binary file to store it's data.
# Specify the path where the whoosh index should live. This should generally
# be ignored by version control
HAYSTACK_WHOOSH_PATH = '/path/to/whoosh.index'
```

#### [openpyxl](http://packages.python.org/openpyxl/)

Avocado comes with an `export` package for supporting various means of exporting data into different formats. One of those formats is the native Microsoft Excel 2007 _.xlsx_ format. To support that, the openpyxl library is used.

Install by doing `pip install openpyxl`.

Read more about [exporting]() in Avocado.

## Configure

At a minimum, your `INSTALLED_APPS` should contain the following apps:

```python
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',

    'modeltree',
    'avocado',
    ...
)
```

### ModelTree Setup

Avocado heavily relies on [ModelTree](http://modeltree.harvest.io) for dynamically query generation. For consistency of joins, a default _root model_ must be defined which acts as a reference point for constructing joins.

In addition to adding `modeltree` to the `INSTALLED_APPS` above, add the following to your project settings:

```python
MODELTREES = {
    'default': {
        'model': 'myapp.SomeModel',
    },
}
```

Confirm that it works by running the `preview` subcommand that comes with ModelTree:

```bash
python manage.py modeltree preview
```

All of the models related to `myapp.SomeModel` will be printed to the console with various indentation levels. This represents the _traversal depth_. There should not be any surprises, but if there are models you would like to exclude, simply add the `excluded_models` key to the settings dict:

```python
MODELTREES = {
    'default': {
        'model': 'myapp.SomeModel',
        'excluded_models': ['auth.User'],
    },
}
```

For greater control over _how_ ModelTree traverses paths, [read the docs](http://modeltree.harvest.io).

### Next: [Getting Started]({{ site.baseurl }}{% post_url 2013-03-02-getting-started %})

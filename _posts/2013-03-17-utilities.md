---
layout: page
title: "Utilities"
category: ref
date: 2013-03-17 00:05:00
---

## Registry & Autodiscover

Django and many third-party apps use the _autodiscover_ pattern for loading code across apps. The idea is to choose a module to check for across in each app and load it for some reason.

Avocado uses this pattern as well for:

- formatters
- translators
- exporters
- interfaces

In each of these cases, the goal is the same: to register classes or instances to be used as choices in the admin. This bridges the gap between code and data by referencing bits of code by name. This of course can be fragile as there are no checks or hard constraints if the underlying class names change.

To make use of this pattern simply do the following:

```python
# foo/mymodule.py
from avocado.core import loader

# If the discovered modules need to register something, initialize
# the registry first
registry = loader.Registry()

# Kick off the autodiscovery. This module itself must be imported
# into a module that is loaded early on by Django such as models.py
loader.autodiscover('mymodule')
```

A module that would be discovered would look like this:

```python
# bar/mymodule.py
from foo.mymodule import registry

class SomeClass(object):
    ...

registry.register(SomeClass)
```

To set a default value for the registry (or override an existing one), pass the `default=True` argument. This will set the name of the entry to `'Default'`.


## Buffered Paginator

Django provides a solid [pagination API](https://docs.djangoproject.com/en/dev/topics/pagination/), but the `Paginator` relies on a list of objects to be passed in.

`BufferedPaginator` is a subclass of the Django `Paginator` class that allows for explicitly setting the `_count` attribute i.e. the total length of `object_list`. This removes the need for the Paginator to perform this calculation on `object_list` which enables reusing a pre-cached value.

```python
from avocado.core.paginator import BufferedPaginator

# Buffered set of objects
buff_list = range(10)

# Total count of 100, 2 per page, offset of 40
paginator = BufferedPaginator(100, buff_list, offset=40, per_page=2)
paginator.num_page # 50
paginator.cached_page_indices() # 21, 26
paginator.cache_pages() # 5

paginator.page(20).in_cache() # False
paginator.page(21).in_cache() # True
paginator.page(26).in_cache() # False
```

The `object_list` (named `buff_list` in the example) that is passed in as an argument represents a *buffered* part of the whole `object_list`. This works in conjunction with the `BufferedPage` which can test whether or not a particular page is actually stored in the `BufferedPaginator` object.

`buf_size` represents the size of the buffer, i.e. number of rows that will be available at any given time and in most cases the size of `object_list` assuming `count` is greater than `buf_size`.

If `object_list` is not passed in, all calculations will still be available, but any operations that act on the `object_list` will throw an error.

The use of the class is primarily for large data sets in which it is impractical to store the entire `object_list` into a paginator or if computing the count or slicing the list (even for QuerySets) is too costly.

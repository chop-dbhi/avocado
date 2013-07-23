---
layout: page
title: "Query Processing Pipeline"
category: doc
date: 2013-06-10 13:49:27
---

_Since 2.0.24_

Avocado provides a `avocado.query.pipeline` package for handling and combining some of the boilerplate setup and interaction between it's APIs for using it as an [end-to-end query pipeline]({{ site.baseurl }}{% post_url 2013-03-17-query-processing %}).

### Query Processors

Currently there is a single class, `QueryProcessor`, that provides a few methods to make it easier for constructing and executing queries. A processor is initialized with an optional set of arguments:

- `context` - A `DataContext` instance
- `view` - A `DataView` instance
- `tree` - A `ModelTree` alias or instance
- `include_pk`- A boolean denoting whether the primary key should be included in the result set. Default is `True`.

```python
from avocado.query import pipeline
processor = pipeline.query_processors.default()

# It also supports key lookups
processor = pipeline.query_processors['default']()
```

#### `get_queryset([queryset], [**kwargs])`

Create a QuerySet based on context, view, and tree. It also takes a `queryset` argument to act as a _base_ queryset to build upon.

```python
queryset = processor.get_queryset()
```

#### `get_iterable([**kwargs])`

Prepare an iterable for the exporter to consume with optional `offset` and `limit` arguments. This calls `get_queryset` internally and passes any `kwargs` provided.

```python
iterable = processor.get_iterable()
```

#### `get_exporter(export_class, [**kwargs])`

Prepare an exporter instance given an exporter class. This passes the `view` provided during initialization to the exporter. If `include_pk` is `True` an additional raw formatter will be inserted to handle the additional value at the beginning of the row.

```python
from avocado.export import CSVExporter
exporter = processor.get_exporter(CSVExporter)
```

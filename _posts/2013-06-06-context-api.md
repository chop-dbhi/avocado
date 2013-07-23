---
layout: page
title: "Context API"
category: ref
date: 2013-06-06 21:26:44
---

Avocado defines a simple structure for representing query conditions. A query condition boils down to three components:

- the `field` to which the condition applies
- the `operator` which defines how the condition is being applied
- the `value` which defines which value(s) are affected by the condition

Just as in a SQL statement, applying conditions to query enables constraining the data to some subset. Conditions can of course be combined using conditional AND or OR operators. These conditional _branches_ join together two or more conditions or other branches resulting in a _tree_ of conditions.

```
     AND
    /   \
  OR     A
 /  \
B    C
```

Using `field`s as the condition's reference point enables applying the tree of conditions to any query.

The `DataContext` model provides a simple API for storing, persisting and applying the condition tree. In it's raw state, the condition tree is simply a combination of _condition_ and _branch_ nodes and is stored internally as JSON data.

An example of it's usage:

```python
>>> from avocado.models import DataContext
>>> cxt = DataContext({'field': 'library.book.price', 'operator': 'gt', 'value': 10.00})
>>> queryset = cxt.apply()
>>> print str(queryset.query)
'SELECT "book"."id", "book"."title", "book"."author_id", "book"."price" FROM "book" WHERE "book"."price" > 10.00 '
```

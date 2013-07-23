---
layout: page
title: "View Facet Validation"
category: wip
date: 2013-06-06 21:26:44
---

## Specification

This is an extension to the core [validation spec]({{ site.baseurl }}{% post_url 2013-03-17-validation %}).

### Constraints

#### Use of `field` vs. `concept`

The `field` and `concept` properties are mutually exclusive since they may represent two different sets of data. If both are defined an error will occur.

### Facet

#### `sort`

The sort direction of the data in ascending (`asc`) or descending (`desc`) order

#### `sort_index`

The index/position for the sort. This defines _when_ the sort is applied for the facet. For example, the below facet list would display _Color_, _Shape_, and _Texture_ data (in that order) sorted by _Texture_ **then by** _Color_:

```javascript
[{
    'field': 'store.product.color',
    'sort': 'desc',
    'sort_index': 1
}, {
    'field': 'store.product.shape'
}, {
    'field': 'store.product.texture',
    'sort': 'asc',
    'sort_index': 0
}]
```

If a `sort` direction, but no `sort_index` is specified for a facet, they are applied (in order) after all other explicitly defined sorts. For example, the below list would sort first by _Shape_ then by _Color_ then by _Texture_:

```javascript
[{
    'field': 'store.product.color',
    'sort': 'asc'
}, {
    'field': 'store.product.shape',
    'sort': 'asc',
    'sort_index': 0
}, {
    'field': 'store.product.texture',
    'sort': 'desc'
}]
```

### Warnings

- `FACET_NOT_ORDERABLE`
    - The facet cannot be ordered.

### Errors

- `FIELD_XOR_CONCEPT_REQUIRED`
    - If both a `field` and `concept` are defined, this error will be returned denoting only one of the two may be defined.

## Examples

### Facet

```python
{
    'concept': 4,
    'sort': 'desc',
    'sort_order': 0,
    'language': 'Pure Tone Average (PTA)'
}
```

### View

_Simply a list of facets._

```python
[{
    'concept': 4,
    'sort': 'desc',
    'sort_index': 0,
    'language': 'Pure Tone Average (PTA)'
}, {
    ...
}]
```

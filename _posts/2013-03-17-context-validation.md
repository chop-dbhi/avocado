---
layout: page
title: "Context Validation"
category: wip
date: 2013-03-17 00:05:00
---

> ### 2013-02-23 - WIP

## Specification

This is an extension to the core [validation spec]({{ site.baseurl }}{% post_url 2013-03-17-validation %}).

### Condition Nodes

- `operator`
    - The operator to be used for the condition
- `value`
    - The value to be used for the condition
- `nulls`
    - A boolean denoting whether to include/exclude `NULL` values if they are allowed for the field.

### Branch Nodes

Branch nodes act as containers for nesting relationship between nodes and are not associated to specific Field or Concept instances. Therefore only the two attributes below are required.

- `children`
    - A list of of nodes (condition or branch)
- `type`
    - The logical relationship between the nodes in the `children` list, either `or` or `and`.

### Warnings

- `VALUE_OUT_OF_RANGE`
    - Applies to numerical values that are greater than the max or less than the min
- `VALUE_NOT_A_CHOICE`
    - Applies to enumerable or key-based data where the value is not in the set
- `VALUE_NOT_NULLABLE`
    - Applies to all fields. If a value does not allow `NULL` values to be stored, but the query is filtering by them, no data will be returned.
- `SINGLE_NODE_BRANCH`
    - Applies to branch nodes that only contain a single node which deems the branch unnecessary. The client should replace the branch node with the single condition.
- `EMPTY_BRANCH`
    - Applies when a branch contains no child nodes

### Errors

- `INVALID_VALUE`
    - The value is of the wrong type or format
- `INVALID_OPERATOR`
    - The operator supplied is not valid for the field
- `INVALID_OPERATOR_FOR_VALUE`
    - The combination of operator and value are invalid, e.g. a range query with a single value

## Examples

### Condition Node

```python
{
    'concept': 4,
    'field': 39,
    'value': 54,
    'operator': 'gt',
    'nulls': False,
    'language': 'Pure Tone Average (PTA) is greater than 54',
    'enabled': False,
    'errors': ('Value out of range',)
}
```

### Branch Node

```python
{
    'type': 'or',
    'children': [{ ... }, { ... }]
}
```

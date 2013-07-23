---
layout: page
title: "API Breakdown"
category: wip
date: 2013-03-02 08:38:03
---

## Data API

`Field`-level API which exposes methods and properties for accessing the data directly.

### Values, Labels, Codes, and Search

- `values` - tuple of distinct values
- `labels` - tuple of distinct labels representing the values
- `codes` - tuple of distinct codes representing the values
- `choices` - tuple of value, label pairs
- `coded_choices` - tuple of code, label pairs (applicable to stats packages such as R and SAS)
- `search` - string-based search using _contains_, _exact_, or _regex_, returns tuple of choices

### Aggregation and Statistics

- `size` - size (count) of distinct values
- `count` - total (non-distinct) count of values
- `max` - max value
- `min` - min value
- `avg` (numbers only) - population average
- `sum` (numbers only) - population sum
- `stddev` (numbers only) - population standard deviation
- `variance` (numbers only) - population variance

## Query API

### Context Nodes

TBD

### View/Facet Nodes

TBD

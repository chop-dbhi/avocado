---
layout: page
title: "Validation"
category: wip
date: 2013-03-17 00:05:00
---

## Implementations

- [Context Validation]({{ site.baseurl }}{% post_url 2013-03-17-context-validation %})
- [View/Facet Validation]({{ site.baseurl }}{% post_url 2013-06-06-view-facet-validation %})

## Process

**Nodes should always be validated prior to use.**

- Nodes are validated and annotated with `warnings` and `errors` if any are determined
- A node is considered _invalid_ if any errors or warnings are associated with it.
- Nodes that are explicitly marked `enabled = False` prior to validation will be ignored.
    - This enables the client to toggle/keep around a slew of nodes that may be invalid or not applicable without impacting the validation and ultimately the query.
- The entire tree/structure is considered invalid if it contains at least one invalid node that is not disabled
- Invalid nodes due to warnings can be forced to be used by setting `enabled = True`, however nodes with errors can never be enabled
    - Until the node is changed or removed, this flag will remain so the node does not get redundantly validated
- The node's natural language representation is annotated for future reference in case the underlying data changes prior to the next access

## Client Usage

- Node structure is passed to the validator
    - Optionally save the structure (with validation annotations)
    - If the node is valid, continue post-validation, such as execution of a query
    - If the node is not valid, return the structure with annotations for remediation

## Specification

These are considered the _common_ attributes across validation. The way they are utilized during validation is node dependent.

- `field`
    - An integer representing the primary key identifer for a `DataField` instance, e.g. `1`
    - Period-delimited string representing a natural key for a `DataField` instance, e.g. `"app.model.field"`
    - An array of strings representing a natural key for a `DataField` instance, e.g. `["app", "model", "field"]`
- `concept`
    - An integer representing the primary key identifier of the `DataConcept` the field is contained in. Clients that take advantage of concepts will likely need to supply this in order to correctly repopulate and/or organize data on the client.
- `language`
    - A string that is a natural language representation of the node. This is annotated server-side and is used for information purposes.
- `enabled`
    -  A boolean that is used during validation of a node on the server. Invalid nodes will have this flag set to `False`. Clients may set this flag to `True` for invalid nodes only with warnings. Setting the flag to `True` for nodes with errors will have no effect.
- `warnings`
    - A read-only array of warnings that result during validation of the node. Warnings are considered unharmful if the corresponding node is applied and should not cause downstream errors.
- `errors`
    - A read-only array of errors that result during validation of the node. Errors _are_ considered harmful as they cause errors downstream.

### Warnings

_No general warnings are defined._

### Errors

- `FIELD_OR_CONCEPT_REQUIRED`
    - Either `field` or `concept` is required
- `FIELD_DOES_NOT_EXIST`
    - The field the node represents no longer exists
- `CONCEPT_DOES_NOT_EXIST`
    - The concep the node represents no longer exists
- `PERMISSION_DENIED`
    - Permission is denied for the field or concept

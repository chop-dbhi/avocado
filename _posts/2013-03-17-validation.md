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

- New or modified nodes are validated
    - Invalid nodes are not saved
    - The node's natural language representation is computed and saved for future reference
        - This enables presenting the node as it was defined at the time of save in case the underlying data or fields have changed in the mean time
- Existing nodes are re-validated upon use
    - Invalid nodes are flagged `enabled = False` to prevent returning an empty or erroneous result set
    - Validation warnings and errors will be annotated on the node directly for client use
- Disabled nodes due to warnings can be forced to be used by setting `enabled = True`, nodes with validation _errors_ however cannot be enabled
    - Until the node is changed or removed, this flag will remain so the node does not get redundantly validated

## Client Considerations

- show error and warning messages per concept/field
- provide remediation options
    - confirm removal for each node with validation errors
        - this will remove the node permanently from the tree
    - for nodes with only warnings, the node can be re-enabled
        - certain use cases may deal with volatile data and the data may be valid _eventually_

## Specification

These are considered the _common_ attributes across validation. The way they are utilized during validation is node dependent.

- `field`
    - An integer representing the primary key identifer for a `DataField` instance, e.g. `1`
    - Period-delimited string representing a natural key for a `DataField` instance, e.g. `"app.model.field"`
    - An array of strings representing a natural key for a `DataField` instance, e.g. `["app", "model", "field"]`
- `concept`
    - An integer representing the primary key identifier of the `DataConcept` the field is contained in. Clients that take advantage of concepts will likely need to supply this in order to correctly repopulate and/or organize data on the client.
- `language`
    - A read-only string that is a natural language representation of the node. This is annotated server-side and is used for information purposes and future validation purposes.
- `enabled`
    -  A boolean that is used during re-validation of the node on the server. If the node is no longer valid due to data changes or the field is not longer available, this flag is set to `false`. Clients may provide the option to override this auto-disabling policy for nodes with only warnings (not errors) by changing the flag to `True`. This is preferred over removing the flag to prevent the re-validation process happening subsequent times. Nodes with errors are recommended to be removed.
- `warnings`
    - A read-only array of warnings that result during re-validation of the node. These are considered warnings since there is no harm in applying the node.
- `errors`
    - A read-only array of errors that result during re-validation of the node. Errors are different from warnings in that the node is considered _broken_ and cannot be enabled. Clients may choose to remove the node from the tree or leave it for historical reasons.

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

---
layout: page
title: "Query Processing"
category: wip
date: 2013-03-17 00:05:00
---

### Pipeline

Avocado provides multiple tailored, but complementary APIs for modifying the way a query gets interpreted, constructed, executed and presented.

#### Parse

Parse, validate and clean core data required for downstream processing. The 'contents' of the conditions are not a concern at this point.

- Validation the format of the input data
    - Error: bad format, cannot process
- Lookup Field and Concept
    - Error: field or concept not found, field not associated with concept
- Check operator is valid and is valid for the supplied value
    - Error: operator is not valid, not valid for value
- Apply access-level permissions
    - Error: permission denied

#### Interpret

Validate and interpret the 'contents' of the conditions. Most interpretation will spout warnings, but some may cause an error if it can be translated into a queryable representation.

- Check the value is within the bounds, a choice from a finite set, etc.
    - Warn: value out of range, value not a choice
- Natural language translation of values
    - Error: cannot translate <source> to <target> language
- Unit conversion
    - Error: units cannot be converted
- Apply data-level permissions
    - Error: permission denied
- Create natural language representation of condition

---

**At this point, the client should not be exposed to any changes due to the below processing. The input data will be agumented with the warnings and errors if any exist.**

#### Augmentation

Apply additional processing to make queries more robust by applying some 'intelligence'.

- Natural language processing (NLP) of values
- Synonym matching
- Domain-specific assumptions

#### Construct

Convert the final cleaned and augmented conditions into Django ORM structures for query construction.

- Build `Q` object for the node
- Convert non-native operators in a ORM consumable component e.g. `QuerySet.extra(...)` keyword arguments
- Build the QuerySet/SQL
- Add additional columns for `SELECT DISTINCT ... ORDER BY` queries where the column was not requested

#### Execute

Execute the query and apply post-fetch processing.

- Remove redundant rows (optional)

#### Present/Package

Format output data based on the requested export method or output format.

- Apply concept formatters to each row

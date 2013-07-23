---
layout: page
title: "Profiles API"
category: wip
date: 2013-06-06 21:26:44
---

The **Profiles API** bring together the various interfaces that Avocado exposes for describing, accessing, and interpreting a data field. These currently include:

- a `DataField` model instances which represents the descriptors and metadata for the field itself
- a data `Interface` (proposal) which exposes the direct data access API at the field-level
- a [query processing]() and interpretation API (supersedes the `Translator` API) which exposes the query parsing, validation, construction, and execution behavior of the field
- a `Formatter` component (not yet defined at the field level) for introducing formatting capabilities

In addition, the Profiles API removes the need to use the database-backend components of Avocado which increases the stability of the API (i.e. a bad data migration won't alter the data API behavior).

Profiles are exposed on the `DataField` or `DataConcept` instances under the `profile` property, although most public API methods will be proxied directly on the instance.

```python
from avocado.models import DataField

f = DataField.init('app.model.field')
f.profile
```

Profiles can be directly registered for model fields:

```python
from avocado import profiles
# Register a custom profile or set of options for the
# default profile.
profiles.register_field('app.model.field', {...})
```

Concepts can be defined similarly:

```python
# Concept name, a list of fields, and an optional profile instance
# or dict of options for the default profile.
profiles.register_concept('some name', ['app.model.field', ...], {...})
```

In either case, the `{...}` can be a `dict` of options passed into the respective `*Profile` class or it can be a `*Profile` instance itself. This enables subclassing and customizing the behavior directly rather than initializing via options.

---
layout: page
title: "Persisting Sets of Objects"
category: guide
date: 2013-03-17 00:05:00
---

_This guide requires [django-objectset](https://pypi.python.org/pypi/django-objectset)_

## Motivation

It is common for saving off sets of objects (e.g. patients) for later reference. This enables performing actions to the set without the need for the original query conditions as well as performing basic set operations such as union and intersection between sets of the same type.

The main benefits include:

- API for creating persistant, on-the-fly sets of objects
- Performance benefits of joining on a fixed set of a objects without the encumbrance of query conditions
- Using sets as building blocks for creating more complicated queries that may be virtually impossible for end users to construct manually otherwise

## Setup

For models that need to be _set-enabled_, the model should subclass `ObjectSet` abstract class. The subclass must implement a `ManyToManyField` pointing to the model of interest:

```python
from objectset.models import ObjectSet

class PatientSet(ObjectSet):
    # Give a name to your sets..
    name = models.CharField(max_length=100)
    patients = models.ManyToManyField(Patient)
```

`ObjectSet` defines three fields of it's own:

- `count` for caching the size of the set
- `modified` for keeping track each time the set changes
- `created` to know when the set is created (timestamps are good)

## Quick Usage

Sets can be initialized with a `QuerySet` or list of existing objects (that are already saved). The constructor also takes an optional `save` flag for immediately saving the set. It can also take the normal field keyword arguments (such as `name`) like a normal model constructor.

```python
qs1 = Patient.objects.filter(...)
pset1 = PatientSet(qs1, save=True)

qs2 = Patient.objects.filter(...)
pset2 = PatientSet(qs2, save=True)

# Patients only in pset1 or pset2, but not both (exclusive or)
pset3 = pset1 ^ pset2
pset3.save()

# In-place operations also work.. remove all patients in
# pset1 from pset2
pset2 -= pset1
pset2.save()
```

## Integration

The main integration point is exposing sets as a means of filtering the object of interest. Again, this enables thinking of sets as building blocks. Perform less complex queries and gradually build up a set of interest.

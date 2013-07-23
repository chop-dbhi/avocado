---
layout: page
title: "Fields vs. Concepts"
category: doc
date: 2013-03-02 08:38:03
order: 4
---

## Fields

Fields represent the _true_ and _pure_ medium for accessing the underlying data. They map directly to single field/column in the database. The level of transformation and/or translation at this level is dependent on the cleanliness of the underlying data. In general it is _always_ better to improve the data directly, rather than relying on manipulation at runtime. However in some cases this is not available for legacy systems.

As with any [typed system](http://en.wikipedia.org/wiki/Type_system), each type has slightly different constraints and capabilities about the data. The goal of transparency is achieved when the API is kept uniform across these types. The subtleties appear in the inputs and outputs for each type.

Ultimately, queries will be constructed and data will be retrieved at the field.

## Concepts

Concepts are an abstraction on top of fields. A concept can be composed of one field or a 1000, but the goal of a concept is represent these fields in a cohesive way.

The most basic (and common) concept is composed of a single field and does not alter the representation of the field's data in any way. Other concepts are composed of multiple fields that have no meaning by themselves, but require the data to the represented together. This is typical of data containing supplementary data such as units of measure or flags. Represented alone, those data are meaningless since there is no context.

By representing fields together, concepts create a better mental map of the underlying data.

---
layout: page
title: "Field Interface"
category: wip
date: 2013-03-17 00:05:00
---

## Abstract

The `FieldInterface` class provides a means of proxying functionality through `Field` instances for type-specific implementations.

## Introduction

The `Field` model can be thought of an extension to Django's model fields. Each `Field` instance is _linked_ to a model field via the `app_name`, `model_name`, and `field_name` properties. Like model fields, depending on the type and constraints of the underlying data properties and methods may need to behave slightly differently. To support this necessary and convenient flexibility the `Field` model can make use of an delegate to a _proxy_ object that implements the properties and methods specific to the field's requirements.

_Note: In this context, this is considered a _natural key_ since in Django does not support apps with the same name and thus will not have any collisions._

Currently, this customization has been achieved with built-in support for various types (e.g. `Lexicon` and `ObjectSet`), but for query purposes, it has been limited to writing a custom `Translator` for the `Field` instance. These means of customization have the following limitations:

- Hard-coded implementation for native field types and extension types such as `Lexicon` and `ObjectSet`
- No ability to customize behavior for new field types or extension types, e.g. `JSONField`
- No ability to finely customize the data-access layer for limiting data access, transforming at runtime, etc.
- No ability to support row-level permissions to data

## Goals

- Port data-related properties and methods from `Field` to `FieldInterface`
- Port `Translator` functionality to `FieldInterface`
- Introduce one or more ways of defining a custom interface for `Field` instances
- Introduce improved validation over the translator API
- Deprecate translator API

## Implementation

- Override `Field.__getattr__` to utilize the `FieldInterface` defined for the instance
- Support dynamically setting an interface object
- Local properties and methods will always be checked for first to prevent overriding core functionality
- `AttributeError` exception will result in a delegation to the `FieldInstance` object for the `Field` instance
    - Attributes with an underscore prefix will not be considered
- The `_interface` property will be lazily initialized
- The `FIELD_INTERFACES` setting is a tuple of class paths
    - This acts as the global set of interface classes across `Field` instances
    - This follows the `AUTHENTICATION_BACKENDS` pattern enabling more specific interface classes to be defined first and eventually falling back to the default one

## Public Specification

### Class Properties & Methods

- `supports_coded_values` - A boolean denoting whether the interface supports coded values. This is currently only used for export by the R and SAS exporters.
- `valid_for_field(field)` - Takes a model field instance and determines if the interface class is appropriate to be used for the field.

### Instance Properties & Methods

#### Core & Utilities

- `model` - The model class this interface will act on. _Note, this will not always be the model the `DataField` represents._
- `field` - The model field this interface will act on. _Note, this will not always be the model field the `DataField` represents._
- `internal_type` - The internal data type of the field.
- `simple_type` - The mapped simple type of the field relative to the `SIMPLE_TYPES` setting.
- `nullable` - Returns whether the field allows `NULL` values. This affects downstream query construction and validation.
- `size(**context)` - Returns the distinct count of values

#### Labelers & Coders

These are helper methods for labeling and coding values.

- `label_for_value(value, **context)` - Returns the corresponding label for `value`.
- `code_for_value(value, **context)` - Returns the corresponding code for `value`.
- `labels_for_values(values, **context)` - Returns an ordered set labels for `values`.
- `codes_for_values(values, **context)` - Returns an ordered set of codes for `values`.

#### Values, Labels, and Codes

Each of the methods below take an optional `iterator` argument which will return an iterator as supposed to loading the results in memory.

- `values(order=True, **context)` - Returns a QuerySet of values
- `labels(order=True, **context)` - Returns a QuerySet of labels
- `codes(order=True, **context)` - Returns a QuerySet of codes
- `choices(order=True, **context)` - Returns a QuerySet of value, label pairs
- `coded_choices(order=True, **context)` - Returns a QuerySet of code, label pairs

#### Search

- `search(query, match='contains', iterator=False, order=True, distinct=True, **context)` - Returns a tuple of value, search (defaults to the label) pairs

#### Utilities

- `value_exists(value, **context)` - Determines if `value` exists.
- `values_exist(values, **context)` - Determines if all `values` exist.

#### Aggregation

- `count(distinct=False, **context)` - Return the count of values
- `max(**context)` - Returns the max value
- `min(**context)` - Returns the min value
- `avg(**context)` - Returns the average (numbers only)
- `sum(**context)` - Return the sum of values (numbers only)
- `stddev(**context)` - Return the standard deviation of values (numbers only)
- `variance(**context)` - Returns the variance of values (numbers only)

## Private Specification

Any property or method starting with an underscore is considered _private_ and will not be accessible by the `DataField` instance using it.

### Instance Properties & Methods

#### Field _Roles_

By default, all of these properties return the base `field`.

- `_value_field` - The field to be used when performing lookups for the underlying data
- `_label_field` - The field that contains the label representation for a value
- `_code_field` - The field that contains a code representation for a value
- `_order_field` - The field to be used when ordering the data
- `_search_field` - The field to be used when performing string-based searches on the data

#### QuerySet Roles

- `_base_queryset(order=True, **context)` - Returns a `QuerySet` of model objects. This method is not generally used directly, but by other methods listed below since this return whole objects and is non-specific to the field. The `**context` keyword arguments (used across all data-producing methods) enables downstream implementation to pass in additional context to whom or what is requesting the underlying data. The base interface class can be overridden to take this into account and restrict access to data based on permission.
- `_values_queryset(distinct=True, **context)` - Returns a `ValuesListQuerySet` of values.
- `_labels_queryset(distinct=True, **context)` - Returns a `ValuesListQuerySet` of labels.
- `_codes_queryset(distinct=True, **context)` - Returns a `ValuesListQuerySet` of codes.

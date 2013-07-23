---
layout: page
title: "Metadata Types"
category: ref
date: 2013-03-02 08:38:03
---

## Structural

Django's model field reference describes the options available for defining model fields. The field's subclass (e.g. `IntegerField`) and the various options passed (e.g. `null=True`) contain structural metadata which can be used to understand a field's constraints.

A simple example of how this is useful is to look at how Django's field validation works. If one attempts to save an integer field with a string value, a `ValidationError` will be thrown complaining about the type. This prevents a downstream database type error.

These constraints facilitate better representation of data fields by providing more context to users. This utlimately reduces the number of assumptions and guesswork required to understand what operations can be performed on the data.

Structural metadata tells the user what type of data should be stored in a model field, along with what types of operations can be performed on the data. Structural metadata only changes when the structure of the database itself is changed.

## Descriptive

For any medium to large size data model, describing and managing each field can be a painstaking task. Fields and data available to end-users for query and representation purposes should be informative. This requires high-quality, descriptive metadata.

Django provides two field options [`verbose_name`](https://docs.djangoproject.com/en/1.4/ref/models/options/#verbose-name) and [`help_text`](https://docs.djangoproject.com/en/1.4/ref/models/options/#help-text) that are descriptive metadata, but are hard-coded in the field definition. This is a limitation if the metadata is managed by another party (client or domain expert) since this must be defined in the code itself.

Avocado provides numerous descriptive fields that enables better defined data fields.

## Administrative

For applications which integrate multiple data sources, it can be useful to keep track of the various source information such as the data's organization, a Uniform Resource Identifier (URI), and access permissions.

Avocado has support for Django's built-in [sites](https://docs.djangoproject.com/en/1.4/ref/contrib/sites/) and [auth](https://docs.djangoproject.com/en/1.4/topics/auth/#permissions) apps enabling course grain (per-site/deployment) and fine grain (per-user) permissions on viewing and modifying data fields.

## Functional

Metadata is generally descriptive, structural, or administrative, but Avocado also introduces a few functional metadata. From Avocado's perspective, these attributes correspond to bits of code that influence data access, transformation, and/or representation.

For example, [concepts]({{ site.baseurl }}{% post_url 2013-03-02-fields-vs-concepts %}) can have a `formatter` specified for _formatting_ the field data. This takes the raw field data as input and outputs it some other way. Changing the `formatter` will change how the data is represented.

Another example are field interfaces. Interfaces are classes that define methods and properties which is the  core functionality of the public API for field instances. Overriding or extending the these methods enables customizing the behavior of the field, such as limiting which data can be accessed by user.

In this respect, these functional metadata are crucial to the usability of the field and concept APIs.

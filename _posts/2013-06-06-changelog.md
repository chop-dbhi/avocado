---
layout: page
title: "Changelog"
category: dev
date: 2013-06-06 21:26:44
order: 1
---

### [2.1.0](https://github.com/cbmi/avocado/tree/2.1) (in development)

### [2.0.25](https://github.com/cbmi/avocado/compare/2.0.24...HEAD) (in development)

- Add support for `-range` operator to date, number, datetime and time types

### [2.0.24](https://github.com/cbmi/avocado/compare/2.0.23...2.0.24)

- Drop NumPy and SciPy dependencies for built-in k-means algorithm
    - This is to simplify the install process and remove heavyweight dependencies for use of a single algorithm
- Move export templates under `avocado/templates` to remove the need to add `avocado.export` to `INSTALLED_APPS`
- Add new `QueryProcessor` class (see [052e7d0](https://github.com/cbmi/avocado/commit/052e7d0b12922d48434229f671f8193f72df9007) for details)
- Change `DataField.search` to _not_ return an iterator
    - This enables downstream slice without needing to evaluate the data structure (primarily for `SearchQuerySet` instances)
- Add `avocado.events` package for simple tracking of events such as accessing a `DataConcept` or `DataField`
- Add `DataQuery` model which represents a joint data structure of a `DataContext` and `DataView`
    - The JSON corresponding to each structure is stored, rather than referencing instances directly. This is for simplicity.
- Add support for n-grams search and fix outstanding search tempalte (see [a5c273e](https://github.com/cbmi/avocado/commit/a5c273e59e0fde80fb3213ccbedaaa4d3406cf8f))
    - Note, re-indexing may take much longer than before since it is now correctly indexing the field values

### [2.0.23](https://github.com/cbmi/avocado/compare/2.0.22...2.0.23)

- Add convenience manager method on `DataView` and `DataContext` for get the default template
    - Improve unicode representation for templates

### [2.0.22](https://github.com/cbmi/avocado/compare/2.0.21...2.0.22)

- Add support for Django 1.5
- Increase minimum version of ModelTree 1.1.5
- Add a Haystack `search_sites` module for convenience when integrating in a project
- Remove default search results size of 10
    - This is arbitrary and has caused confusion that it was truncating results
- Augment the `language` text directly to `DataContext` JSON attributes
    - This reduces the overhead for clients to parse the language dict separately
- Modify context validation to disable invalid nodes
    - This takes a more passive approach to validating context nodes, but prevents the context from getting in an unusable state. Validation errors result in the node being disabled.
- Add `template` and `default` fields to DataContext and DataView
    - This enables the use case of differentiating template contexts and views vs. user-defined ones. The `default` flag enables marking a template as the default one to be used so there is a starting point for clients.
- The dict representing the JSON data can be passed into the `DataContext` and `DataView` constructors directly for convenience
    - Other field values can still be defined using keyword arguments `DataContext({...}, name='My Context')`
- Modify verbose name for 'in' to be 'is either X, Y or Z' and the negated form to 'is neither X, Y, nor Z'
- Change container-based operators to use the `Exact` and `NotExact` text for single value lists

### [2.0.21](https://github.com/cbmi/avocado/compare/2.0.20...2.0.21)

- Backport context node schema from 2.1
    - This is a backwards compatible port of the context node changes in Avocado 2.1 specifically to:
        - Support the `field` key instead of `id` as the field identifier
        - Support the `concept` key which is used to scope the `field`
        - Support branches without children or one child to act as containers

### [2.0.20](https://github.com/cbmi/avocado/compare/2.0.19...2.0.20)

- Fix possible mis-ordering of formatter keys and fields

### [2.0.19](https://github.com/cbmi/avocado/compare/2.0.18...2.0.19)

- Add implementation (and fix) for handling the SELECT DISTINCT/ORDER BY behavior in databases more transparently 

### [2.0.18](https://github.com/cbmi/avocado/compare/2.0.17...2.0.18)

- Fix #67, change `ObjectSet` `created` and `modified` to not be auto-updated
- Increase length of `DataField` `app_name`, `model_name`, and `field_name`
    - For extra *long* field names...
- Change `avocado init` to not prepend the model name to the field name
- Fix and ensure unicode throughout
- Fix the admin action for creating a single `DataConcept` from multiple fields when only one field is selected

### [2.0.17](https://github.com/cbmi/avocado/compare/2.0.16...2.0.17)

- Fix performance in `Formatter` class due to redundant logging
- Add support for `Decimal` types in `Formatter.to_number` method

### [2.0.16](https://github.com/cbmi/avocado/compare/2.0.15...2.0.16)

- Update ModelTree to version 1.1.3 (critical bug fix)
- Add receiver for change Avocado settings during test execution
- Add missing `DataField.coded_values` which the `Formatter.to_coded` relied on

### [2.0.15](https://github.com/cbmi/avocado/compare/2.0.14...2.0.15)

- Add backup utilities for performing metadata data migrations
- New command `avocado migration` for creating a metadata fixture and a corresponding South migration to load the fixture
- Fix bug in R and SAS exporters
- Improve `ObjectSet` class to enable deleting set objects rather than just flagging as being deleted
    - Pass the flag `delete=True` when calling a remove-based command, e.g. `foo.replace(objs, delete=True)`

### [2.0.14](https://github.com/cbmi/avocado/compare/2.0.13...2.0.14)

- Fix bug that only checked for NumPy for the for SciPy feature

### [2.0.13](https://github.com/cbmi/avocado/compare/2.0.12...2.0.13)

- Change `HTMLFormatter` to require the `template` argument which may be a template name
or a `Template` object.
- Allow arbitrary `*args` and `**kwargs` to be passed into `*Exporter.write` and
`*Exporter.read` to enable propagation from `write` to `read`
- Add `short_name` and `long_name` for use downstream by clients
- Add [export-specific format as the first *preferred format*](https://github.com/cbmi/avocado/commit/e9865e6631bc62fc63d6cea439dd6d61f4d930d5)
    - This is a better default which enables specific formatting when needed. The more general format can be reused across formatters, but when very specific formatting is necessary, this default is preferred.
- Refactor `DataField.model` and `DataField.field` to take in account `Lexicon` and `ObjectSet` models
    - The *real* field and model instances are now named `real_field` and `real_model`, respectively.
- Fix #55, `Lexicon.label` is now correctly used by the `DataView`
- Rename `sync` subcommand to `init`
- Rename `SYNC_ENUMERABLE_MAXIMUM` to `ENUMERABLE_MAXIMUM`
- Remove `orphaned` command in favor of new `check` that performs multiple setup
checks as well as check for invalid datafields.
- Remove `searchable` model field since this applies only to text-based fields.
    - This has been repurposed as a deprecated computed property
- Fix #45, allow dict-based settings to be updated, but not overridden
- Remove `DataField.data_source` field
    - There was no functional utility of this field and is (currently) out of the scope for Avocado

### [2.0.12](https://github.com/cbmi/avocado/compare/2.0.11...2.0.12)

- Rename `SasExporter` => `SASExporter` for caps consistency

### [2.0.11](https://github.com/cbmi/avocado/compare/2.0.10...2.0.11)

- Remove assumption of lowercasing the `app_name` during an init call

### [2.0.10](https://github.com/cbmi/avocado/compare/2.0.9...2.0.10)

- String formatting cleanup
- Add missing avocado/export/models.py file form 2.0.9
- Replace `DataField.operators` with `DataField.operator_choices`
    - There is no need for two properties where one is a subset of the other
- Fix `Translator.language` to use the cleaned value for model-based values
- Simplify exact-based `Operator.verbose_name` strings
- Add CHANGELOG to this README :)

### [2.0.9](https://github.com/cbmi/avocado/compare/2.0.8...2.0.9)

- Add appropriate `content_type` and `file_extension` to Exporter classes
- Subclass `DjangoJSONDecoder` for use in the `JSONExporter`
- Add `validate` convenience method to `DataContext` and `DataView`
- Rename `node` to `parse` on `DataContext` and `DataView`
- Add support for [handling redundant rows via the exporter API](https://github.com/cbmi/avocado/issues/43)
    - The `BaseExporter.read` now has a `force_distinct` argument that can be set to `False` to prevent removing redundant rows
- Add (fix) support for using `key`-based `DataField`s
- Refacor R and SAS exporter classes to use templates when generating the script
- Fix `Condition.field` property to use `get_by_natural_key`

### [2.0.8](https://github.com/cbmi/avocado/compare/2.0.7...2.0.8)

- [Add `DataConcept.sortable` field](https://github.com/cbmi/avocado/commit/a7d6e7ca44bb408021c478484721741dbe5351ae)
    - This is purely for informational purposes and does not add a hard constraint when performing ordering by the `DataView`. Clients can use this field to prevent sorting by unsortable concepts.

### [2.0.7](https://github.com/cbmi/avocado/compare/2.0.6...2.0.7)

- Implement settings and management command and [history API (#41)](https://github.com/cbmi/avocado/issues/41)
- Update ModelTree to 1.1.1, make South a hard dependency

### [2.0.6](https://github.com/cbmi/avocado/compare/2.0.5...2.0.6)

- [Abstract out core functionality of DataContext and DataView models](https://github.com/cbmi/avocado/commit/eed56830fd2c1639bf2743da29a2dad2eaaadeb4)
- Fix bug in `legacy` command where a trailing comma caused legacy fields names to be set as a tuple

### [2.0.5](https://github.com/cbmi/avocado/compare/2.0.4...2.0.5)

- Enforce a `SELECT DISTINCT` by default when calling `DataContext.apply`
    - A new keyword argument `default` [has been added](https://github.com/cbmi/avocado/commit/f3b7de08ecd94c36bcefaf7cc3b30cefcc09d44b) to override this behavior
- Wrap `orphaned` command in transaction in case `--unpublish` is used to prevent inconsistent unpublishing
- [Add support for `isnull` lookups](https://github.com/cbmi/avocado/commit/e7686081537f44631703c7638ab06ca1bf401719)

### [2.0.4](https://github.com/cbmi/avocado/compare/2.0.3...2.0.4)

- Add Python 2.6 classifier
- Fix incorrect use of `sys.version_info`

### [2.0.3](https://github.com/cbmi/avocado/compare/2.0.2...2.0.3)

- Add Python 2.6 support

### [2.0.2](https://github.com/cbmi/avocado/compare/2.0.1...2.0.2)

- Change django-jsonfield dependency link to cbmi fork

### [2.0.1](https://github.com/cbmi/avocado/compare/2.0.0...2.0.1)

- Fix setup.py classifiers
- Fix django-jsonfield dependency link

### 2.0.0 - Initial release

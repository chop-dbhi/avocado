# Avocado
#### _Metadata APIs for Django_

- [Target Audience]
- [Background]
- [Install]
- [Configure]
- [Getting Started]
- [Examples]
- [Notes]

## Target Audience

**Developers who are interested in letting their data do the work for them.**

Some experience with Django is necessary, run through the [model docs](https://docs.djangoproject.com/en/1.4/topics/db/models/) (and possibly the [tutorial](https://docs.djangoproject.com/en/1.4/intro/tutorial01/)) if you are unfamiliar with Django. Some general Python experience is necessary.

## Background

Django models provides the **structural** metadata necessary for interfacing with the supported database backends. However, in general, there is no formal mechanism to supply **descriptive** or **administrative** metadata about your data model. Avocado is a Django app which provides metadata management for your models.

Avocado grew out of projects being developed in a clinical research environment where data models can often be large and complex. Additionally, there are frequently data fields that contain related, but decoupled data which typically results in a large hierarchical data model.

When developing applications that make use of such data, developers need to be able to provide end-users with appropriate context and representation of the data elements to avoid confusion and errors of omission.

### A Real Example

All this abstract talk can be a bit confusing, so here is an example. In medicine, it's typical that results from a diagnostic test like a blood test might be broken into several columns in a relational database: a numerical value, units of measure, and an assessment as to whether it is normal, high, or low. As a developer you'd like to be able to bundle these conveniently in your application.

While you could just store them all as one text field in your database, that sacrifices the ability to query and perform mathematical calculations on the numerical field. On the other hand, splitting them apart means a user who does not know your data model very well needs to know upfront to hunt down the various elements on their own, or they risk getting an incomplete picture of the retrieved data.

In many cases, these kinds of complexities result in a research workflow where the technical team act as "keepers of the data", and all the researcher's questions are filtered through them to be translated into queries. This situation, while good for the continued employment of engineers, is not ideal for open-ended discovery and hypothesis generation by researchers.

### The Solution

Avocado was designed to support the development of accessible, transparent, and data-rich applications by providing several major capabilities:

- A formal means of storing additional metadata for your data model
- Robust API's for interrogating metadata for dynamic query generation which includes translation, validation, cleaning and execution of queries
- Built-in extensible components for the formatting and exporting of data

The power of Avocado's dynamic query generation lies in it's ability to [span relationships transparently](#transparent-relationships). This allows users (and to some extent developers) to focus on the data and not have to worry about the data model.

### Target Applications

While Avocado can be useful for any project, it is likely to be most applicable to projects with a heavy focus on data, especially ones with query, reporting, and export requirements and/or with medium to large data models. As a developer, it can be very useful as a tool for _accessing_ some data for the first time. For users, it is most intended for applications focused on domain-specific data discovery.

### Types of Metadata

#### Structural

Django's model field reference describes the options available for defining model fields. The field's subclass (e.g. `IntegerField`) and the various options passed (e.g. `null=True`) contain structural metadata which can be used to understand a field's constraints.

A simple example of how this is useful is to look at how Django's field validation works. If one attempts to save an integer field with a string value, a `ValidationError` will be thrown complaining about the type. This prevents a downstream database type error.

These constraints facilitate better representation of data fields by providing more context to users. This utlimately reduces the number of assumptions and guesswork required to understand what operations can be performed on the data.

#### Descriptive

For any medium to large size data model, describing and managing each field can be a painstaking task. Fields and data available to end-users for query and representation purposes should be informative. This requires high-quality, descriptive metadata.

Django provides two field options [`verbose_name`](https://docs.djangoproject.com/en/1.4/ref/models/options/#verbose-name) and [`help_text`](https://docs.djangoproject.com/en/1.4/ref/models/options/#help-text) that are descriptive metadata, but are hard-coded in the field definition. This is a limitation if the metadata is managed by another party (client or domain expert) since this must be defined in the code itself.

Avocado provides numerous descriptive fields that enables better defined data fields.

#### Administrative

For applications which integrate multiple data sources, it can be useful to keep track of the various source information such as the data's organization, a Uniform Resource Identifier (URI), and access permissions.

Avocado has support for Django's built-in [sites](https://docs.djangoproject.com/en/1.4/ref/contrib/sites/) and [auth](https://docs.djangoproject.com/en/1.4/topics/auth/#permissions) apps enabling course grain (per-site/deployment) and fine grain (per-user) permissions on viewing and modifying data fields.

---

## Prerequisites

As of now, Python 2.7 is required. Want older versions supported? Fork the repo and submit a pull request.

To install Avocado and it's dependencies, it is assumed you have the latest versions of [distribute](http://pypi.python.org/pypi/distribute) (or [setuptools](http://pypi.python.org/pypi/setuptools)) and [Pip](http://pypi.python.org/pypi/pip) installed.

## Install

```
pip install avocado
```

The _hard_ dependencies which will auto-install are [Django 1.4+](https://www.djangoproject.com), [modeltree 1.0+](http://pypi.python.org/pypi/modeltree) and [django-jsonfield 0.9+](https://github.com/bradjasper/django-jsonfield/).

## Optional Dependencies

For a bare-bones Avocado installation the following dependencies may be skipped, but peruse through to understand the purpose of each one listed.

_Have a suggestion for additional metadata integration? [File an issue](https://github.com/cbmi/avocado/issues/new) on Avocado's GitHub repo._

#### [Django "sites" Framework](https://docs.djangoproject.com/en/1.4/ref/contrib/sites/)
Having this installed enables associating `DataField`s and/or `DataConcept`s to specific sites, or more specifically, deployments. For example, an internal and external deployment may exist for the same application, but only the internal deployment provides access to certain _restricted_ fields for operational use.

Install by adding `django.contrib.sites` to `INSTALLED_APPS`.

#### [django-guardian](http://packages.python.org/django-guardian/)
This enables fine-grain control over who has permissions for various `DataField`s. Permissions can be defined at a user or _group_ level.

Install by doing `pip install django-guardian` and adding `guardian` to `INSTALLED_APPS`.

#### [django-haystack](http://haystacksearch.org)
What's having all this great descriptive data if no one can find it? Haystack provides search engine facilities for the metadata.

Install by doing `pip install django-haystack` and installing one of the supported search engine backends. The easiest to setup is [Whoosh](http://pypi.python.org/pypi/Whoosh) which is implemented in pure Python. Install it by doing `pip install whoosh`. Add `haystack` to `INSTALLED_APPS`.

#### [SciPy](http://www.scipy.org)
Avocado comes with a `stats` package for performing some rudimentary statistical, aggregation and clustering operations on the data. This is not always required or necessary for all data, but if there is a heavy emphasis on numerical data or the amount of data is quite large, the `stats` may come in handy.

Install by doing `pip install numpy` first (a dependency of SciPy), followed by `pip install scipy`. Note, there are a few dependencies for compilation, so review [SciPy's installation instructions](http://www.scipy.org/Installing_SciPy) for more details.

#### [openpyxl](http://packages.python.org/openpyxl/)
Avocado comes with an `export` package for supporting various means of exporting data into different formats. One of those formats is the native Microsoft Excel _.xlsx_ format. To support that, the openpyxl library is used.

Install by doing `pip install openpyxl`.

## Configure

At a minimum, your `INSTALLED_APPS` should contain the following apps:

```python
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',

    'avocado',
    ...
)
```

---

## Getting Started

To introduce the API gradually and coherently, we are going to start with two example models, `Author` and `Book` in an app named `library`.

```python
# library/models.py
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author)
    pub_date = models.DateField('publication date', null=True)
```

### Bootstrap the Metadata

To reiterate the introduction above, Avocado is about putting in place ways to define and make use of metadata surrounding your data model.

Avocado comes with a `sync` subcommand which introspects Django models and creates `DataField` instances representing the model fields. At least one app label (`library`) or model label (`library.book`) must be specified.

By default, `DataField` instances are not created for primary and foreign key fields. In practice, surrogate key fields are used infrequently as is, thus they are not created by default. To override this behavior and include key fields, add the flag `--include-keys`.

Likewise, model fields may be marked as not being editable in the model field definitions. This flag is turned on typically for operational or bookkeeping fields such as timestamps. By default, `DataField`s are not created for these either, but can overridden by passing the `--include-non-editable`.

```
./manage.py avocado sync library
1 field added for Author
2 fields added for Book
```

On a side note, the `avocado` command acts as a parent for various subcommands. Simply type `./manage.py avocado` to show a list of available subcommands.

### DataField API

An Avocado `DataField` instance represents a single Django model field instance. These three attributes uniquely identify a model field instance.

- `f.app_name` - The name of the app this field's model is defined in
- `f.model_name` - The name of the model this field is defined for
- `f.field_name` - The attribute name of the field on the model

```python
>>> from avocado.models import DataField
>>> f = DataField.objects.get_by_natural_key('library', 'book', 'title')
>>> f
<DataField 'library.book.title'>
>>> f.app_name
'library'
>>> f.model_name
'book'
>>> f.field_name
'title'
```

These three attributes enable referencing to the actual field instance and model class:

- `f.field` - The model DataField instance this field represents
- `f.model` - The model class this field is associated with

```python
>>> f.field
<django.db.models.fields.CharField at 0x101b5fe10>
>>> f.model
<class 'library.models.Book'>
```

#### Descriptors

Additional metadata can be defined for this object to make it more useful to humans. Define various _descriptors_ to enhance the meaning of a data field.

- `f.name` - A verbose human readable name of the field
- `f.name_plural` - The plural form of the verbose name. If not defined, an _s_ will be appended to `f.name` when the plural form is accessed.
- `f.description` - A long description for the field
- `f.keywords` - Other related keywords (this is primarily applicable for search indexing by django-haystack)
- `f.unit` - The unit of the data, for example _gram_
- `f.unit_plural` - The plural form of the unit, for example _grams_. If not defined, an _s_ will be appended to `f.unit` when the plural form is accessed.

```python
>>> f.name = 'Price'
# f.name_plural can be set, but does not need to be since
# this is a simple plural form
>>> f.get_plural_name()
'Prices'
# likewise with the f.unit_plural..
>>> f.unit = 'dollar'
>>> f.get_plural_unit()
'dollars'
```

#### Data Properties

`DataField`s also acts as an interface and exposes various properties and methods for directly accessing the underlying data or properties about the data.

- `f.enumerable` - A flag denoting if the data in this field is composed of an enumerable set. During a [sync](avocado-sync), each field's data is evaluated based on the internal type and the size of the data (number of distinct values). By default, if the field is a `CharField` and is has `SYNC_ENUMERABLE_MAXIMUM`
- `f.internal_type` - The low-level datatype of the field. This is really only used for mapping to the below `simple_type`. Read more about the [internal vs. simple types].
- `f.simple_type` - The high-level datatype of the field used for validation purposes and as general metadata for client applications. (These types can be overridden, [read about](SIMPLE_TYPE_MAP) the `SIMPLE_TYPE_MAP` setting)
- `f.size` - Returns the number of _distinct_ values for this field. The `__len__` class hook uses this attribute under the hood.
- `f.values` - Returns a tuple of distinct raw values ordered by the field
- `f.mapped_values` - Returns a tuple of distinct values that have been mapped relative to the `DATA_CHOICES_MAP` setting and unicoded.
- `f.choices` - A tuple of pairs zipped from `f.values` and `f.mapped_values`. This is useful for populating form fields for client applications.
- `f.query()` - Returns a `ValuesQuerySet` for this field. This is equivalent to `f.model.objects.values(f.field_name)`.

```python
>>> f.internal_type
'char'
>>> f.simple_type
'string'
>>> f.size # len(f) also works..
33
>>> f.values
('A Christmas Carol', 'A Tale of Two Cities', 'The Adventures of Oliver Twist', ...)
>>> f.mapped_values
(same as above...)
>>> f.choices
(('A Christmas Carol', 'A Christmas Carol'), ...)
>>> f.query()
[{'title': 'A Christmas Carol'}, ...]
```

#### Data Aggregations

A simple, yet powerful set of methods are available for performing aggregations. Each method below returns an `Aggregator` object which enables chaining aggregations together as well as adding conditions to filter or exclude results.

- `f.count([*groupby])` - Returns a count of all values for the field
- `f.max([*groupby])` - Returns the max value
- `f.min([*groupby])` - Returns the min value
- `f.avg([*groupby])` - Returns the average of all values
- `f.sum([*groupby])` - Returns the sum of all values
- `f.stddev([*groupby])` - Returns the standard deviation of all values. _This is not supported in SQLite by default._
- `f.variance([*groupby])` - Returns the variance of all values. _This is not supported in SQLite by default._

Standalone evaluations:

```python
>>> price = DataField.objects.get_by_natural_key('library', 'book', 'price')
>>> price.count()
33
>>> price.max()
132.00
>>> price.min()
14.50
>>> price.avg()
32.25
>>> price.sum()
1064.25
```

Each aggregation method can take Avocado or standard QuerySet lookup strings to group by those fields.

```python
>>> price.count('book__author')
[{'author': 'Charles Dickens', 'count': 4}, ...]
>>> price.avg('book__author')
[{'author': 'Charles Dickens', 'avg': 50.45}, ...]
```

The methods are chainable, the only caveat is that the `*groupby` arguments must be the same across all the aggregation methods. To bypass this, use the `groupby()` method to affix the group by fields.

```python
>>> price.count().avg().sum()
{'count': 33, 'avg': 32.25, 'sum': 1064.25}
>>> price.groupby('book__author').count().avg().sum()
[{'author': 'Charles Dickens', 'count': 4, 'avg': 50.45, 'sum': 201.80}, ...]
```

Additional methods are available for filtering, excluding and ordering the data.

```python
>>> price.count('book__author').filter(count__gt=50).order_by('count')
```

---

## The DataContext

Avocado defines a simple structure for representing query conditions. A query condition boils down to three components:

- the `datafield` to which the condition applies
- the `operator` which defines how the condition is being applied
- the `value` which defines which value(s) are affected by the condition

Just as in a SQL statement, applying conditions to query enables constraining the data to some subset. Conditions can of course be combined using conditional AND or OR operators (not the same operators mentioned above). These conditional _branches_ join together two or more conditions or other branches resulting in a _tree_ of conditions.

```
     AND
    /   \
  OR     A
 /  \
B    C
```

Using `datafield`s as the condition's reference point enables applying the tree of conditions to any query.

The `DataContext` model provides a simple API for storing, persisting and applying the condition tree. In it's raw state, the condition tree is simply a combination of _condition_ and _branch_ nodes. Following this example, the schema of both node types are described.

```python
>>> from avocado.models import DataContext
>>> cxt = DataContext()
# This will be serialized (and validated) to JSON when saved
>>> cxt.json = {'id': 'library.book.price', 'operator': 'gt', 'value': 10.00}
>>> queryset = cxt.apply()
>>> print str(queryset.query)
'SELECT "book"."id", "book"."title", "book"."author_id", "book"."price" FROM "book" WHERE "book"."price" > 10.00 '
```

#### Condition Node

##### `id`
The value can be:

- An `int` representing the primary key identifer for a `DataField` instance, e.g. `1`
- Period-delimited `string` representing a natural key for a `DataField` instance, e.g. `'app.model.field'`
- An `array` of strings representing a natural key for a `DataField` instance, e.g. `["app", "model", "field"]`

##### `operator`
A `string` representing a valid `DataField` operator. Valid operators vary depending on the implementation and are validated downstream. If not specified, the operator defaults to `exact`.

##### `value`
Any valid JSON data type.

#### Branch Node

##### `type`
A `string` that is `"and"` or `"or"` representing the type of branch or logical operation between child nodes defined in the `children` property.

##### `children`
An `array` of _two_ or more nodes.

_See example [DataContext Condition Trees]_

---

## APIs

### Translators

Translators are used to modify query conditions prior to being executed. Depending on the quality or variability of your data, the query interface for a field may not represent the data 1:1 with the underlying data. Thus the incoming query condition may need to be translated in some way to work with the underlying database.



These operator classes perform only light validation of the value to prevent being too restrictive.

```python
>>> from avocado.query.operators import registry as operators
>>> iexact = operators.get('iexact')
>>> iexact.is_valid(['hello', 'world'])
False
>>> iexact.is_valid('hello world')
True
>>> inlist = operators.get('inlist')
>>> inlist.is_valid(['hello', 'world'])
True
>>> inlist.is_valid('hello world')
False
```

The base `Translator` class uses [Django's Form API](https://docs.djangoproject.com/en/1.4/ref/contrib/forms/api/) to validate and clean the value relative to the underlying model field (e.g. `f.field`).

The primary method to call is `translate` which calls `clean_value` and `clean_operator`.

```python
>>> t = Translator()
>>> t.translate(f, 'icontains', 'Python')
{
    'condition': <django.db.query_utils.Q at 0x1027b78d0>,
    'annotations': {},
    'cleaned_data': {
        'operator': 'icontains',
        'value': u'Python',
    },
    'raw_data': {
        'operator': 'icontains',
        'value': 'Python',
    },
}
```

### Coded Values

Some consumers of data require (or prefer) string values to be represented, or _coded_, as a numerical value. A runtime enumerated mapping of values (e.g. 'foo' → 1, 'bar' → 2) would typically suffice for one-off data exports, but for managing data exports over time as new data is loaded, keeping the mappings fixed improves cross-export compatibility.

Avocado provides a simple extension is this behavior is desired.

1. Add `'avocado.coded'` to `INSTALLED_APPS`
2. Build the index of coded values `./bin/manage.py avocodo coded`

---

## DataConcepts

### Introduction

As much as Avocado is a metadata management tool, a prime consumer of this metadata are humans. More specifically, the metadata can be used to provide more context and meaning to the data and the data model.

The notion of a `DataConcept` came from the need to represent discrete data in a human-readable domain-specific way. Data is typically stored in a normalized, discrete and efficient way, thus rendering it a bit obscure in it's raw state. Sometimes a single _column_ of data in database table is meaningless without another column, for example a column of `weight` without the column of `unit`.

Of course, data must be stored in this discrete way to ensure the database can treat it properly and perform the correct operations on that data. Unfortunately, humans don't care about how data is stored, nor should they. **They simply want the data to be accessible so they can consume it in a way that makes sense to them.**

Concepts encapsulate one or more fields intended to be represented together in some way. This sounds very abstract and is intentionally so. This lightweight abstract encourages being creative in how fields are represented together.

### Query Views

#### Datatypes

Datatypes, in the context of Avocado, are used for representation of the data for querying, not for data entry. Differentiating between datatypes such as `int` vs. `float` are typically too specific for data discovery, thus these related native types are rolled up into a high-level datatype, such as `number`.

- `string`
- `number`
- `date`
- `boolean`

### Formatters

The most common utility of the DataConcept abstraction is formatting the fields' data in a usable format for the consumer. The consumer may be a human, a Web browser, an R interpreter or anything else. Regardless of the consume, formatters provide an API for taking in raw data and outputting a representation of that data.

The most common utility of the `DataConcept` abstraction is formatting the fields' data in a usable format for the consumer. The consumer may be a human, a Web browser, an R interpreter or anything else. Regardless of the consume, formatters provide an API for taking in raw data and outputting a representation of that data.

```python
from avocado.formatters import Formatter
# Get the 'Dosage' concept which combines the 'dose'
# and 'unit' fields
dosage = DataConcept.objects.get(name='Dosage')
# Prepare a formatter for the dosage concept
formatter = Formatter(dosage)
values = [60, 'mg', 'as needed']
# Returns ['60', 'mg', 'as needed']
formatter(values, preferred_formats=['string'])
```

A formatter attempts to solve two problems. First, **coerce the various values into the preferred format** and secondly, perform an operation on each or all of the values. As shown above, the `formatter` instance is callable and takes a sequence of `values` and a `preferred_formats` argument. Since this is the base formatter class, aside from being good at coercing datatypes, it is not terribly useful.

Formatters can be easily created by subclassing the base `Formatter` class and adding, overriding, or augmenting the methods. As stated above, a formatter can be applied each raw value or all values together. As an example of this, we can create a simple `ConcatFormatter`.

```python
class ConcatFormatter(Formatter):
    def to_string(self, values, cfields, **context):
        joined = ' '.join(map(lambda x: super(ConcatFormatter, self).to_string(x),
                values.values()))
        return OrderedDict({'output': joined})

    # Informs the class this method can process multiple values at a time
    to_string.process_multiple = True
```

### Exporters

---

## Management Commands

Avocado technically has a single command `./bin/manage.py avocado`. The commands listed below are subcommands of the `avocado` command.

### sync

The sync command creates DataField instances from Djang model fields. This will be used whenever new models or new fields are added to your data model.

```bash
./bin/manage.py avocado sync labels [--update] [--include-keys] [--include-non-editable]
```

#### Parameters

- `labels` - refers to one or more space-separated app or model labels, for example library.book refers the the model Book in the app library.
- `--update` - updates existing field instances (relative to the apps or models defined and overwrites any existing descriptive values such as name, name_plural, and description.
- `--include-non-editable` - creates field instance for model fields with editable=False (by default these are ignored).
- `--include-keys` - creates fields instances for primary and foreign key fields (by default these are ignored).

### orphaned

Checks for DataField instances that no longer map to Django model field (like a dead hyperlink).

```bash
./bin/manage.py avocado orphaned [--unpublish]
```

#### Parameters

`--unpublish` - unpublishes all fields found to be orphaned.

## Settings

Avocado settings are defined as a dictionary, named `AVOCADO`, with each key corresponding to a setting listed below:

```python
AVOCADO = {
	'SIMPLE_TYPE_MAP': { ... },
	'SYNC_ENUMERABLE_MAXIMUM': 50,
	...
}
```

### SIMPLE_TYPE_MAP

`DataField` datatypes from Avocado's perspective are used purely as metadata for the purposes of making the underlying data accessible.

This setting is used to customize what is returned by the `f.datatype` property. The default datatype comes from the internal datatype of a the model field's `get_internal_type()` method. Any of these default datatypes can be mapped to some other datatype.

Datatypes in this context should be simple, for example not differentiating between `int`, `float`, or `Decimal`. They are all just numbers, to that is the datatype.

These datatypes help define how input is validated and which operators are allowed.

The default map:

```
# A mapping between model field internal datatypes and sensible
# client-friendly datatypes. In virtually all cases, client programs
# only need to differentiate between high-level types like number, string,
# and boolean. More granular separation be may desired to alter the
# allowed operators or may infer a different client-side representation
SIMPLE_TYPE_MAP = {
    'auto': 'number',
    'biginteger': 'number',
    'decimal': 'number',
    'float': 'number',
    'integer': 'number',
    'positiveinteger': 'number',
    'positivesmallinteger': 'number',
    'smallinteger': 'number',

    'nullboolean': 'boolean',

    'char': 'string',
    'email': 'string',
    'file': 'string',
    'filepath': 'string',
    'image': 'string',
    'ipaddress': 'string',
    'slug': 'string',
    'text': 'string',
    'url': 'string',
}
```

### OPERATOR_MAP

```
# A mapping between the client-friendly datatypes and sensible operators
# that will be used to validate a query condition. In many cases, these types
# support more operators than what are defined, but are not include because
# they are not commonly used.
OPERATOR_MAP = {
    'boolean': ('exact', '-exact', 'in', '-in'),
    'date': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'number': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'string': ('exact', '-exact', 'iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'),
    'datetime': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
    'time': ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range'),
}
```

### RAW_DATA_MAP

```
# Contains a mapping from raw data values to a corresponding human
# readable representation. this will only ever be applicable when values
# are being presented to client programs as potential choices
RAW_DATA_MAP = {
    None: 'Null',
    '': '(empty string)',
}
```

### INTERNAL_TYPE_FORMFIELDS

```
# A general mapping of formfield overrides for all subclasses. the mapping is
# similar to the SIMPLE_TYPE_MAP, but the values reference internal
# formfield classes, that is integer -> IntegerField. in many cases, the
# validation performed may need to be a bit less restrictive than what the
# is actually necessary
INTERNAL_TYPE_FORMFIELDS = {
    'auto': 'IntegerField',
    'integer': 'FloatField',
    'positiveinteger': 'FloatField',
    'positivesmallinteger': 'FloatField',
    'smallinteger': 'FloatField',

    # Generic datatypes mapped from above
    'number': 'FloatField',
}
```

### SYNC_ENUMERABLE_MAXIMUM

```
# The maximum number of distinct values allowed for setting the
# `enumerable` flag on `DataField` instances during the `sync` process. This
# will only be applied to fields with non-text strings types and booleans
SYNC_ENUMERABLE_MAXIMUM = 30
```

---

# Optional App Integration

## [South](http://south.aeracode.org/)
Django's de facto app for creating and managing database migrations. 'nuff said.

## [django-haystack](http://haystacksearch.org/)
Avocado utilizes Haystack for building search indexes for `DataField` and `DataConcept` objects and their underlying data. In practice, this is primarily used for clients exposing a search feature for finding the `DataField` or `DataConcept` representations for some data.

## [django-activity-stream](http://justquick.github.com/django-activity-stream/)
Avocado is about supporing data discovery and iteration by providing APIs for rapidly implementing interfaces, enabling this workflow. Many of our in-house applications have made good use of tracking users' own discovery and iteration progress. In practice, this acts as a history/log of a user's discovery workflow. This can be useful for users and developers alike.

If this app is installed, changes to `DataContext` and `Query` objects will trigger actions to be sent to the respective user's stream.

## [Numpy](http://numpy.scipy.org/) & [SciPy](http://www.scipy.org/)
Avocado has support for clustering continuous numeric values when generating distribution queries.
---

# Examples

## DataContext Condition Trees

#### Single Condition

```javascript
{
	"id": 2,
	"operator": "iexact",
	"value": 50
}
```

#### Branch with Two Conditions

```javascript
{
	"type": "and",
	"children": [{
		"id": 2,
		"operator": "iexact",
		"value": 50
	}, {
		"id": 1,
		"operator": "in",
		"value": ["foo", "bar"]
	}
}
```

#### Branch with One Condition and One Branch

```javascript
{
	"type": "or",
	"children": [{
		"id": 2,
		"operator": "iexact",
		"value": 50
	}, {
		"type": "and",
		"children": [{
			"id": 1,
			"operator": "in",
			"value": ["foo", "bar"]
		}, {
			"id": 1,
			"operator": "in",
			"value": ["baz", "qux"]
		}]
	}]
}
```

## Notes

### Internal vs. Simple Types

Internal types correspond to the model field's class and are necessary when performing write operations for data intregrity. For query purposes, internal types tend to be too _low-level_ and restrictive during query validation. To provide a less restrictive interface for query validation, Avocado introduces a _simple_ type which merely maps internal types to a higher-level type such as _string_ or _number_.

### Relationships Are Transparent [transparent-relationships]

Avocado uses the [ModelTree](https://github.com/cbmi/modeltree) API to build in-memory indexes for each model accessed by the application. To build an index, all possible paths from the given _root_ model are traversed and metadata about each relationship is captured. When a query needs to be generated, the lookup string can be generated for a model field relative to the root model.

```python
>>> tree = ModelTree(Author)
>>> title = Book._meta.get_field_by_name('title')
>>> tree.query_string_for_field(title, 'icontains')
'book__title__icontains'
```

This looks a bit clumsy in practice which is why Avocado uses the `DataField` class to manage all this field-specific _stuff_.

Having these indexes enables generating queries regardless of the entry point and which fields are being queried or retrieved. This perceivably _flattens_ out the data model from the client's perspective which increases it's accessiblity.
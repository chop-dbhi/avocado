# Avocado

#### Metadata APIs for Django

## Target Audience

**Developers who are interested in letting their data do the work for them.**

#### Before you begin:
- Some general Python experience is necessary.
- Some experience with Django is necessary. If you are unfamiliar with Django, the [tutorial](https://docs.djangoproject.com/en/1.4/intro/tutorial01/) is an excellent place to start, or you can look into the [model docs](https://docs.djangoproject.com/en/1.4/topics/db/models/). 

## Background

Django models provides the **structural** metadata necessary for interfacing with the supported database backends. However, in general, there is no formal mechanism to supply **descriptive** or **administrative** metadata about your data model. Avocado is a Django app which provides easy metadata management for your models.

Avocado grew out of projects developed in a clinical research environment, where data models are frequently very large and complex. Additionally in this setting, there are data fields that contain related but decoupled data. This typically results in a large hierarchical data model, which can get pretty messy pretty quickly.

When developing applications that make use of this type of data, developers need to be able to provide end-users with appropriate context and representation of the data elements to avoid confusion and errors of omission.

### A Real Example

All this abstract talk can be a bit confusing, so lets jump into an example. In medicine, it's typical that results from a diagnostic test like a blood test might be broken into several columns in a relational database: a numerical value, units of measure, and an assessment as to whether it is normal, high, or low. As a developer you'd like to be able to bundle these conveniently in your application.

While you could just store them all as one text field in your database, that sacrifices the ability to query and perform mathematical calculations on the numerical field. On the other hand, splitting them apart means a user who does not know your data model very well needs to know upfront to hunt down the various elements on their own, or they risk getting an incomplete picture of the retrieved data.

In many cases, these kinds of complexities result in a research workflow where the technical team act as "keepers of the data", and all the researcher's questions are filtered through them to be translated into queries. This situation, while good for the continued employment of engineers, is not ideal for open-ended discovery and hypothesis generation by researchers.

### The Solution

Avocado was designed to support the development of accessible, transparent, and data-rich applications by providing several capabilities:

- A formal way to store additional metadata for your data model
- Robust API's for interrogating metadata for dynamic query generation which includes translation, validation, cleaning, and execution of queries
- Built-in extensible components for the formatting and exporting of data

The power of Avocado's dynamic query generation lies in it's ability to [span relationships transparently](#relationships-are-transparent). This allows users (and to some extent developers) to focus on the data and not have to worry about the data model.

### Target Applications

While Avocado can be useful for any project, it is most likely applicable to projects with a heavy focus on data. As a developer, it can be very useful as a tool for _accessing_ some data for the first time. For users, it is most useful for applications focused on domain-specific data discovery.

### Types of Metadata

#### Structural

Django's model field reference describes the options available for defining model fields. The field's subclass (e.g. `IntegerField`) and the various options passed (e.g. `null=True`) contain structural metadata which can be used to understand a field's constraints.

A simple example of how this is useful is to look at how Django's field validation works. If one attempts to save an integer field with a string value, a `ValidationError` will be thrown complaining about the type. This prevents a downstream database type error.

These constraints facilitate better representation of data fields by providing more context to users. This utlimately reduces the number of assumptions and guesswork required to understand what operations can be performed on the data.

Structural metadata tells the user what type of data should be stored in a model field, along with what types of operations can be performed on the data. Structural metadata only changes when the structure of the database itself is changed.

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

To introduce the API, we are going to get started with two example models, `Author` and `Book` in an app named `library`.

```python
# library/models.py
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author)
    pub_date = models.DateField('publication date', null=True)
    price = models.DecimalField('Book price', decimal_places=2)
```

### Bootstrap the Metadata

To reiterate the introduction above, Avocado is about defining metadata and making use of existing metadata surrounding your data model.

Avocado comes with a `init` subcommand which introspects Django models and creates `DataField` instances representing the model fields. At least one app label (`library`) or model label (`library.book`) must be specified.

By default, `DataField` instances are not created for primary and foreign key fields. In practice, surrogate key fields are used infrequently as is, thus they are not created by default. To override this behavior and include key fields, add the flag `--include-keys`.

Likewise, model fields may be marked as not being editable in the model field definitions. This flag is turned on typically for operational or bookkeeping fields such as timestamps. By default, `DataField` instances are not created for these either, but can be overridden by passing the `--include-non-editable`.

```bash
./manage.py avocado init library
1 field added for Author
2 fields added for Book
```

**Note:** The `avocado` command acts as a parent for various subcommands. Simply type `./manage.py avocado` to show a list of available subcommands.

### DataField API

An Avocado `DataField` instance represents a single Django model field instance. These three attributes uniquely identify a model field.

- `f.field_name` - The name of the field on the model
- `f.model_name` - The name of the model this field is defined for
- `f.app_name` - The name of the app this field's model is defined in

```python
>>> from avocado.models import DataField
>>> f = DataField(field_name='title', model_name='book', app_name='library')
>>> f
<DataField 'library.book.title'>
```

These three attributes allow you to access the actual field instance and model class:

- `f.field` - The model DataField instance this field represents
- `f.model` - The model class this field is associated with

```python
>>> f.field
<django.db.models.fields.CharField at 0x101b5fe10>
>>> f.model
<class 'library.models.Book'>
```

#### Descriptors

Additional metadata can be defined for this object to make it more useful to users. Define various _descriptors_ to enhance meaning of a data field.

- `f.name` - A verbose human-readable name of the field
- `f.name_plural` - The plural form of the verbose name. If not defined, an _s_ will be appended to `f.name` when the plural form is accessed provided `f.name` does not already end with _s_.
- `f.description` - A long description for the field
- `f.keywords` - Other related keywords (this is primarily applicable for search indexing by [django-haystack](#django-haystack))
- `f.unit` - The unit of the data, for example _gram_
- `f.unit_plural` - The plural form of the unit, for example _grams_. If not defined, an _s_ will be appended to `f.unit` when the plural form is accessed, provided `f.unit` does not already end with _s_.

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

#### Properties

A `DataField` also acts as an interface that exposes various properties and methods for directly accessing the underlying data or properties about the data.

##### Editable

- `f.enumerable` - A flag denoting if the field's data is composed of an enumerable set. During a [init](avocado-init), each field's data is evaluated based on the internal type and the size of the data (number of distinct values). By default, if the field is a `CharField` and has `ENUMERABLE_MAXIMUM` or less distinct values, this will be set to `True`. 

##### Read-only

- `f.internal_type` - The low-level datatype of the field. This is really only used for mapping to the `simple_type`, displayed below. Read more about the [internal vs. simple types](#internal-vs-simple-types).
- `f.simple_type` - The high-level datatype of the field used for validation purposes and as general metadata for client applications. (These types can be overridden, [read about](SIMPLE_TYPE_MAP) the `SIMPLE_TYPE_MAP` setting)
- `f.size` - Returns the number of _distinct_ values for this field
- `f.values_list` - Returns a `ValuesQuerySet` of distinct values for the field.
This is primarily used by the functions below. Useful when you want to apply additional QuerySet operations.
- `f.values` - Returns a tuple of distinct raw values ordered by the field. If the corresponding model is a subclass of Avocado's `Lexicon` abstract model, the order corresponds to the `order` field on the `Lexicon` model subclass. Read more about the [`Lexicon` abstract class](#lexicon-abstract-class).
- `f.labels` - Returns a unicoded tuple of labels. If the corresponding model is a subclass of Avocado's `Lexicon` abstract model, this corresponds to the `label` field on the `Lexicon` model subclass. Read more about the [`Lexicon` abstract class](#lexicon-abstract-class).
- `f.choices` - A tuple of pairs zipped from `f.values` and `f.labels`. This is useful for populating form fields for client applications.
- `f.searchable` (DEPRECATED) - A flag denoting if the field's data should be treated as searchable text. This applies to `TextField`s and `CharField`s which are not marked as `enumerable`.

```python
>>> f.internal_type
'char'
>>> f.simple_type
'string'
>>> f.size
33
>>> f.values
('A Christmas Carol', 'A Tale of Two Cities', 'The Adventures of Oliver Twist', ...)
>>> f.labels
(u'A Christmas Carol', u'A Tale of Two Cities', u'The Adventures of Oliver Twist', ...)
>>> f.choices
(('A Christmas Carol', u'A Christmas Carol'), ...)
>>> f.values_list
['A Christmas Carol', 'A Tale of Two Cities', 'The Adventures of Oliver Twist', ...]
```

##### Lexicon &amp; ObjectSet

In addition to the above `DataField` API, instances that represent a 
`Lexicon` or `ObjectSet` class can utilize the `f.objects` property, normally
only available to `Model` classes. It will return a `QuerySet` of the model
it represents:

```python
>>> f = DataField(app_name='dates', model_name='month', field_name='id')
>>> f.objects
[<Month: 'January'>, <Month: 'February'>, ...]
```

Read more about Lexicons and ObjectSets in the DataView API section below.

#### Aggregation

A simple, yet powerful set of methods are available for performing aggregations. Each method below returns an `Aggregator` object which enables chaining aggregations together as well as adding conditions to filter or exclude results.

By default, aggregations are table-wide. Zero or more lookups can be supplied to perform the aggregation relative to the fields in the `GROUP BY`.

- `f.count([*groupby], distinct=False)` - Returns a count of all values for the field. If `distinct` is `True`, a `COUNT(DISTINCT foo)` will be performed.
- `f.max([*groupby])` - Returns the max value
- `f.min([*groupby])` - Returns the min value
- `f.avg([*groupby])` - Returns the average of all values
- `f.sum([*groupby])` - Returns the sum of all values
- `f.stddev([*groupby])` - Returns the standard deviation of all values. _This is not supported in SQLite by default._
- `f.variance([*groupby])` - Returns the variance of all values. _This is not supported in SQLite by default._

Table-wide aggregations:

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

Additional methods are available for filtering, excluding and ordering the data. Each aggregation that is chained is named after the aggregation applied. As shown below, the count aggregation can be used in the subsequent `filter` and `order_by` methods.

```python
>>> price.count('book__author').filter(count__gt=50).order_by('count')
```

### Translators
Translators are useful for converting values before querying the database. Say for instance that we want to be able to query our database based on a patient age, but we are only storing the patients date of birth. We can write a translator to convert the patient age to the appropriate birthdate to get the correct results from the query.

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
>>> from avocado.query.translators import Translate
>>> from avocado.models import DataField

>>> f = DataField.objects.get('library', 'book', 'title')

>>> t = Translator()
>>> t.translate(f, 'icontains', 'Python')
{
    'id': 2,
    'operator': 'icontains',
    'value': 'Python',
    'cleaned_data':{
        'operator': <Operator: "contains the text" (icontains)>,
        'value': u'Python',
        'language': u'Book title contains the text Python',
    }
    'query_modifiers':{
        'condition': <django.db.query_utils.Q at 0x1027b78d0>,
        'annotations': None,
        'extra': None 
    }
}
```

## DataConcept API

### Introduction

As Avocado is a metadata management tool, it is important to note that metadata is most useful to end-users who can readily access it. More specifically, the metadata can be used to provide more context and meaning to the data and the data model, enabling end-users to get the most out of their data.

The notion of a `DataConcept` came from the need to represent discrete data in a readable, domain-specific way. Data, however, is typically stored in a normalized, discrete and efficient way, making it a bit difficult for users to fully understand. For example, sometimes a single _column_ of data in a database table is meaningless without another column, such as a database storing medicine prescriptions with a column of `dose` without the columns of `unit` and `interval`. 

Data must be stored in a discrete way to ensure the database can treat it properly and perform the correct operations on the data. Unfortunately, most users don't always know how their data is stored in the database; they are only interested in accessing their data in a way that makes sense to them and allows them to use their data in a meaningful way. `DataConcept`s help solve this problem.

`DataConcept`s encapsulate one or more fields intended to be represented together in some way. This allows users to combine their fields in a way that makes the most sense for how they want to use their data given their current context. For example, we could create a `DataConcept` for dosage that would represent `dose`, `unit`, and `interval` together.

Here is an example showing how we would create a `DataConcept` called `Dosage` for our prescriptions database.

 ```python
>>> from avocado.models import DataConcept, DataField, DataConceptField
# Create the 'Dosage' DataConcept which combines the 'dose'
# 'unit', and 'interval' fields
>>> concept = DataConcept(name='Dosage')
>>> concept.save()

# Get the DataFields for the 'dose', 'unit', and 'interval'
# fields
>>> dose = DataField.objects.get_by_natural_key('models', 'prescriptions', 'dose')
>>> unit = DataField.objects.get_by_natural_key('models', 'prescriptions', 'unit')
>>> interval = DataField.objects.get_by_natural_key('models', 'prescriptions', 'interval')
# Recall, the DataFields are populated when you call 
# './manage.py avocado init'

# Add the DataFields to the DataConcept
>>> DataConceptField(concept=concept, field=dose).save()
>>> DataConceptField(concept=concept, field=unit).save()
>>> DataConceptField(concept=concept, field=interval).save()
```

### Query Views

#### Datatypes

Datatypes, in the context of Avocado, are used for representation of the data for querying, not for data entry. Differentiating between datatypes such as `int` vs. `float` are typically too specific for data discovery, thus these related native types are rolled up into a high-level datatype, such as `number`.

- `string`
- `number`
- `date`
- `boolean`

### Formatters

The most common utility of the `DataConcept` abstraction is formatting the fields' data in a usable format for the consumer. The consumer may be a human, a Web browser, an R interpreter or anything else. Regardless of the consumer of the data, formatters provide an API for taking in raw data and outputting a representation of that data.

```python
>>> from avocado.formatters import Formatter
# Get the 'Dosage' concept which combines the 'dose'
# 'unit', and 'interval' fields
>>> dosage = DataConcept.objects.get(name='Dosage')
# Prepare a formatter for the dosage concept
>>> formatter = Formatter(dosage)
>>> values = [60, 'mg', 'as needed']
# Returns ['60', 'mg', 'as needed']
>>> formatter(values, preferred_formats=['string'])

# The formatter can also be assigned
```

A formatter attempts to solve two problems: 
- Coerce the various values into the preferred format 
- Perform an operation on each or all of the values 

As shown above, the `formatter` instance is callable and takes a sequence of `values` and a `preferred_formats` argument. Since this is the base formatter class, it is only useful for coercing datatypes.

Formatters can be easily created by subclassing the base `Formatter` class and adding, overriding, or augmenting the methods. As stated above, a formatter can be applied to each raw value or all values together. As an example of this, we can create a simple `ConcatFormatter`.

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

For data export support add `avocado.export` to `INSTALLED_APPS`.

Here is an example of the API:

```python
from avocado.export import CSVExporter

exporter = CSVExporter(concepts)
output = exporter.write(rows)
```

`rows` is an iterable of iterables (e.g. rows from a database query) that will
be chunked up and formatted by the `concepts`. Here is a ASCII visual:

```
chunks:         |    c1   |      c2      | c3 |
row values:     | v1 | v2 | v3 | v4 | v5 | v6 |
```

The length of a chunk corresponds to the number of fields associated with a
concept. `c1` (the first two values) will be formatted by `concept1`'s
formatter, `c2` (next three values) with `concept2`, etc.

---

## DataContext API

Avocado defines a simple structure for representing query conditions. A query condition boils down to three components:

- the `datafield` to which the condition applies
- the `operator` which defines how the condition is being applied
- the `value` which defines which value(s) are affected by the condition

Just as in a SQL statement, applying conditions to query enables constraining the data to some subset. Conditions can of course be combined using conditional AND or OR operators (not the same operators mentioned above). These conditional _branches_ join together two or more conditions or other branches resulting in a _tree_ of conditions.
DataContext
```
     AND
    /   \
  OR     A
 /  \
B    C
```

Using `datafield`s as the condition's reference point enables applying the tree of conditions to any query.

The `` model provides a simple API for storing, persisting and applying the condition tree. In it's raw state, the condition tree is simply a combination of _condition_ and _branch_ nodes. Following this example, the schema of both node types are described.

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

- `id` - The value can be:
    - An `int` representing the primary key identifer for a `DataField` instance, e.g. `1`
    - Period-delimited `string` representing a natural key for a `DataField` instance, e.g. `'app.model.field'`
    - An `array` of strings representing a natural key for a `DataField` instance, e.g. `["app", "model", "field"]`
- `operator` - A `string` representing a valid `DataField` operator. Valid operators vary depending on the implementation and are validated downstream. If not specified, the operator defaults to `exact`.
- `value` - Any valid JSON data type.

#### Branch Node

- `type` - A `string` that is `"and"` or `"or"` representing the type of branch or logical operation between child nodes defined in the `children` property.
- `children` - An `array` of _two_ or more nodes.
    - _See example [DataContext Condition Trees]_

---

## DataView API

---

## Lexicon Abstract Class

Avocado defines an abstract class named `Lexicon`. It is a common practice
when normalizing a data model to _break out_ repeated finite sets of terms
within a column into their own table. This is quite obvious for entities such
as _books_ and _authors_, but less so for commonly used or enumerable
terms.

```
id | name | birth_month
---+------+------------
 1   Sue    May
 2   Joe    June
 3   Bo     Jan
 4   Jane   Apr
...
```

The above shows a table with three columns `id`, `name` and `birth_month`.
There are some inherent issues with `birth_month`:

1. Months have an arbitrary order which makes it very difficult to order the
rows by `birth_month` since they are ordered lexicographically
2. As the table grows (think millions) the few bytes of disk space each
repeated string takes up starts having a significant impact
3. The cost of querying for the distinct months within the population gets
increasingly more expensive as the table grows
4. As the table grows, the cost of table scans increases since queries are
acting on strings rather than an integer (via a foreign key)

Although the above example is somewhat contrived, the reasons behind this
type of normalization are apparent.

To implement, subclass and define the `value` and `label` fields.

```python
from avocado.lexicon.models import Lexicon

class Month(Lexicon):
    label = models.CharField(max_length=20)
    value = models.CharField(max_length=20)
```

A few of the advantages include:

- define an arbitrary `order` of the items in the lexicon
- define a integer `code` which is useful for downstream clients that
prefer working with a enumerable set of values such as SAS or R
- define a verbose/more readable label for each item
    - For example map _Jan_ to _January_

In addition, Avocado treats Lexicon subclasses specially since it is such a
common practice to use them. They are used in the following ways:

- performing a `init` will ignore the `label`, `code`, and `order`
fields since they are supplementary to the `value` (you can of course add them
manually later)
- the `DataField` that represents the `value` field on a Lexicon subclass will
    - use the `order` field whenever accessing values or when applied to a query
    - use the `label` field when accessing `f.labels`
    - use the `code` field when accessing `f.codes`

---

## Object Sets

It is common for saving off sets of objects (e.g. patients) for later reference. This enables performing actions to the set without the constraints of the query conditions as well as performing basic set operations such as union and intersection between sets of the same type.

The main benefits include:

- API for creating persistant, on-the-fly sets of objects (effectively materialized views)
- Performance benefits of joining on a fixed set of a objects without the encumbrance of query conditions
- Using sets as building blocks for creating more complicated queries that may be virtually impossible for end users to construct manually otherwise

For models that need to be _set-enabled_, the model should subclass `ObjectSet` which will make it easier elsewhere to make use of such models. The subclass must implement a `ManyToManyField` pointing to the model of interest.

The usage should look like this:

```python
from avocado.sets import ObjectSet, SetObject

class PatientSet(ObjectSet):
    patients = models.ManyToManyField(Patient, through='PatientSetObject')


class PatientSetObject(SetObject):
    # The db_column overrides are certainly not necessary, but makes the
    # column names a bit more readable when writing raw queries..
    object_set = models.ForeignKey(PatientSet, db_column='set_id')
    set_object = models.ForeignKey(Patient, db_column='object_id')
```

The main integration point is exposing sets as a means of filtering the object of interest. 

- female patients
- less than 5 years of age
- who are in my "african americans with conductive hearing loss" set

This translates to a `DataContext` that looks like this:

```javascript
{
    "type": "and",
    "children": [{
        "id": 1, // sex datafield
        "operator": "exact",
        "value": "female"
    }, {
        "id": 2, // age datafield
        "operator": "lt"
        "value": 5
    }, {
        "id": 3, // patientset datafield
        "operator": "exact",
        "value": 30 // patientset id
    }]
}
```

Although it may be queried and exposed as querying on the set itself, the actually query being executed must join from `Patient` &rarr; `PatientSetObject` where `set_id = 30`. The translator must map from an `ObjectSet` subclass to it's respective M2M through model. The output SQL would look something like:

```sql
SELECT ... some columns ...
FROM "patient" INNER JOIN "patientsetobject" ON ("patient"."id" = "patientsetobject"."object_id")
WHERE "patient"."sex" = 'female' AND "patient"."age" < 5 AND "patientsetobject"."set_id" = 30
```

---

## Template Tags

Avocado provides single base templatetag (similar to the management commands). The syntax is as follows:

```django
{% avocado [command] [arguments] %}
```

### Load
Currently, the only avocado template tag command implemented is the `load` command for loading `DataField` and `DataConcept` instances on demand:

**DataField with primary key**
```django
{% avocado load field 10 as foo %}
```

**DataField using a natural key**
```django
{% avocado load field "app.model.field" as foo %}
```

**DataConcept with a primary key**
```django
{% avocado load concept 20 as foo %}
```

#### Example

This enables using the metadata dynamically in templates through the API, which is documented above.

```django
{% avocado load field "library.author.name" as author %}

<select name="authors">
{% for value, label for author.choices %}
    <option value="{{ value }}">{{ label }}</option>
{% endfor %}
</select>
```

---

## Management Commands

Avocado commands are namespaced under `avocado`. Execute `./bin/manage.py avocado` to view a list of available subcommands.

### init

The init command creates `DataField` instances from Django model fields. This will be used whenever new models or new fields are added to your data model.

```bash
./manage.py avocado init labels [--force] [--include-keys] [--include-non-editable]
```

**Parameters**

- `labels` - refers to one or more space-separated app, model or field labels, for example library.book refers the the model Book in the app library.
- `--force` - forces an update to existing field instances (relative to the apps or models defined and overwrites any existing descriptive values such as name, name_plural, and description.
- `--include-non-editable` - creates field instance for model fields with editable=False (by default these are ignored).
- `--include-keys` - creates fields instances for primary and foreign key fields (by default these are ignored).

### check

Performs Avocado setup and optional dependency checks. It also checks for
`DataField` instances that no longer map to Django model fields
(like a dead hyperlink).

```bash
./manage.py avocado check [--output=html]
```

**Parameters**

`--output` - Specify the output type of the report. Options are `html` or `stdout`.
Default is `stdout`.


### data

Finds all models referenced by the app or model ``labels`` and updates data-related properties such as caches and pre-calculated values.

```bash
./manage.py avocado data labels [--modified]
```

**Parameters**

- `labels` - refers to one or more space-separated app, model, or field labels, for example library.book refers the the model Book in the app library.
- `--modified` - Updates the `data_modified` on `DataField` instances corresponding the labels. This is primarily used for cache invalidation.

**Note, currently `--modified` is the only flag that does anything**

### cache

Finds all models referenced by the app, model or field `labels` and explicitly updates various cached properties relative to the `data_modified` on `DataField` instances.

### history

Tools for managing Avocado's exposed history API.

```bash
./manage.py avocado history [--prune]
```

**Parameters**

- `--prune` - Prunes the oldest archived objects based on the `HISTORY_ENABLED` and `HISTORY_MAX_SIZE` settings.

## Settings

Avocado settings are defined as a dictionary, named `AVOCADO`, with each key corresponding to a setting listed below:

```python
AVOCADO = {
    'SIMPLE_TYPE_MAP': { ... },
    'ENUMERABLE_MAXIMUM': 50,
    ...
}
```

### SIMPLE_TYPE_MAP

`DataField` datatypes from Avocado's perspective are used purely as metadata for the purposes of making the underlying data accessible.

This setting is used to customize what is returned by the `f.simple_type` property. The default datatype comes from the internal datatype of a the model field's `get_internal_type()` method. Any of these default datatypes can be mapped to some other datatype.

Datatypes in this context should be simple, for example not differentiating between `int`, `float`, or `Decimal`. They are all just numbers, to that is the datatype.

These datatypes help define how input is validated and which operators are allowed.

### OPERATOR_MAP

A mapping between the client-friendly datatypes and sensible operators
that will be used to validate a query condition. In many cases, these types
support more operators than what are defined, but are not include because
they are not commonly used.

### INTERNAL_TYPE_FORMFIELDS

A general mapping of formfield overrides for all subclasses. the mapping is
similar to the SIMPLE_TYPE_MAP, but the values reference internal
formfield classes, that is integer -> IntegerField. in many cases, the
validation performed may need to be a bit less restrictive than what the
is actually necessary

### ENUMERABLE_MAXIMUM

The maximum number of distinct values allowed for setting the
`enumerable` flag on `DataField` instances during the `init` process. This
will only be applied to fields with non-text strings types and booleans

### HISTORY_ENABLED

Flag for enabling the history API.

### HISTORY_MAX_SIZE

The maximum size of a user's history. If the value is an integer, this
is the maximum number of allowed items in the user's history. Set to
`None` (or 0) to enable unlimited history. Note, in order to enforce this
limit, the `avocado history --prune` command must be executed to remove
the oldest history from each user based on this value.

---

## Examples

### DataContext Condition Trees

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

### Relationships Are Transparent

Avocado uses the [ModelTree](https://github.com/cbmi/modeltree) API to build in-memory indexes for each model accessed by the application. To build an index, all possible paths from the given _root_ model are traversed and metadata about each relationship is captured. When a query needs to be generated, the lookup string can be generated for a model field relative to the root model.

```python
>>> tree = ModelTree(Author)
>>> title = Book._meta.get_field_by_name('title')
>>> tree.query_string_for_field(title, 'icontains')
'book__title__icontains'
```

This looks a bit clumsy in practice which is why Avocado uses the `DataField` class to manage all this field-specific _stuff_.

Having these indexes enables generating queries regardless of the entry point and which fields are being queried or retrieved. This perceivably _flattens_ out the data model from the client's perspective which increases it's accessiblity.

## CHANGELOG

2.0.13 [diff](https://github.com/cbmi/avocado/compare/2.0.12...2.0.13)

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

2.0.12 [diff](https://github.com/cbmi/avocado/compare/2.0.11...2.0.12)

- Rename `SasExporter` => `SASExporter` for caps consistency

2.0.11 [diff](https://github.com/cbmi/avocado/compare/2.0.10...2.0.11)

- Remove assumption of lowercasing the `app_name` during an init call

2.0.10 [diff](https://github.com/cbmi/avocado/compare/2.0.9...2.0.10)

- String formatting cleanup
- Add missing avocado/export/models.py file form 2.0.9
- Replace `DataField.operators` with `DataField.operator_choices`
    - There is no need for two properties where one is a subset of the other
- Fix `Translator.language` to use the cleaned value for model-based values
- Simplify exact-based `Operator.verbose_name` strings
- Add CHANGELOG to this README :)

2.0.9 [diff](https://github.com/cbmi/avocado/compare/2.0.8...2.0.9)

- Add appropriate `content_type` and `file_extension` to Exporter classes
- Subclass `DjangoJSONDecoder` for use in the `JSONExporter`
- Add `validate` convenience method to `DataContext` and `DataView`
- Rename `node` to `parse` on `DataContext` and `DataView`
- Add support for [handling redundant rows via the exporter API](https://github.com/cbmi/avocado/issues/43)
    - The `BaseExporter.read` now has a `force_distinct` argument that can be set to `False` to prevent removing redundant rows
- Add (fix) support for using `key`-based `DataField`s
- Refacor R and SAS exporter classes to use templates when generating the script
- Fix `Condition.field` property to use `get_by_natural_key`

2.0.8 [diff](https://github.com/cbmi/avocado/compare/2.0.7...2.0.8)

- [Add `DataConcept.sortable` field](https://github.com/cbmi/avocado/commit/a7d6e7ca44bb408021c478484721741dbe5351ae)
    - This is purely for informational purposes and does not add a hard constraint when performing ordering by the `DataView`. Clients can use this field to prevent sorting by unsortable concepts.

2.0.7 [diff](https://github.com/cbmi/avocado/compare/2.0.6...2.0.7)

- Implement settings and management command and [history API (#41)](https://github.com/cbmi/avocado/issues/41)
- Update ModelTree to 1.1.1, make South a hard dependency

2.0.6 [diff](https://github.com/cbmi/avocado/compare/2.0.5...2.0.6)

- [Abstract out core functionality of DataContext and DataView models](https://github.com/cbmi/avocado/commit/eed56830fd2c1639bf2743da29a2dad2eaaadeb4)
- Fix bug in `legacy` command where a trailing comma caused legacy fields names to be set as a tuple

2.0.5 [diff](https://github.com/cbmi/avocado/compare/2.0.4...2.0.5)

- Enforce a `SELECT DISTINCT` by default when calling `DataContext.apply`
    - A new keyword argument `default` [has been added](https://github.com/cbmi/avocado/commit/f3b7de08ecd94c36bcefaf7cc3b30cefcc09d44b) to override this behavior
- Wrap `orphaned` command in transaction in case `--unpublish` is used to prevent inconsistent unpublishing
- [Add support for `isnull` lookups](https://github.com/cbmi/avocado/commit/e7686081537f44631703c7638ab06ca1bf401719)

2.0.4 [diff](https://github.com/cbmi/avocado/compare/2.0.3...2.0.4)

- Add Python 2.6 classifier
- Fix incorrect use of `sys.version_info`

2.0.3 [diff](https://github.com/cbmi/avocado/compare/2.0.2...2.0.3)

- Add Python 2.6 support

2.0.2 [diff](https://github.com/cbmi/avocado/compare/2.0.1...2.0.2)

- Change django-jsonfield dependency link to cbmi fork

2.0.1 [diff](https://github.com/cbmi/avocado/compare/2.0.0...2.0.1)

- Fix setup.py classifiers
- Fix django-jsonfield dependency link

2.0.0 - Initial release

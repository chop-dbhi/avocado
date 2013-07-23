---
layout: page
title: "Getting Started"
category: doc
date: 2013-03-02 08:38:03
order: 2
---

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

To reiterate the [introduction]({{ site.baseurl }}{% post_url 2013-03-02-introduction %}), Avocado is about making the best use of data model's metadata and expanding on that basis.

Avocado comes with a `init` subcommand which introspects Django models and creates `DataField` instances representing the model fields.

By default, `DataField` instances are not created for primary and foreign key fields. In practice, [surrogate key](http://en.wikipedia.org/wiki/Surrogate_key) fields are used infrequently as is, thus they are not created by default. To override this behavior and include key fields, add the flag `--include-keys`.

Likewise, model fields may be marked as not being editable in the model field definitions. This flag is turned  used typically for operational or bookkeeping fields such as timestamps. By default, `DataField` instances are not created for these either, but can be overridden by passing the `--include-non-editable`.

Run the `init` subcommand to create the fields:

```bash
python manage.py avocado init library
1 field added for Author
2 fields added for Book
```

_**Note:** The `avocado` command acts as a parent for various subcommands. Simply type `python manage.py avocado` to show a list of available subcommands._

## DataFields

So what is a `DataField`? A `DataField` instance represents a single Django [model field instance](https://docs.djangoproject.com/en/1.5/ref/models/fields/#field-types). These three attributes uniquely identify a model field.

- `f.app_name` - The name of the app this field's model is defined in
- `f.model_name` - The name of the model this field is defined for
- `f.field_name` - The name of the field on the model

```python
>>> from avocado.models import DataField
>>> f = DataField.init('library', 'book', 'title')
>>> f
<DataField 'library.book.title'>
```

These three attributes allow you to access the actual field instance and model class:

- `f.field` - The Django model field this DataField instance represents
- `f.model` - The model class of the field

```python
>>> f.field
<django.db.models.fields.CharField at 0x101b5fe10>
>>> f.model
<class 'library.models.Book'>
```

### Descriptors

Additional metadata can be defined for this object to make it more useful to users. Define various _descriptors_ to enhance meaning of a data field.

- `f.name` - A verbose human-readable name of the field. This will be derived from the model field's `verbose_name` value by default.
- `f.name_plural` - The plural form of the verbose name. If not defined, an _s_ will be appended to `f.name` when the plural form is accessed provided `f.name` does not already end with _s_.
- `f.description` - A long description for the field. This will be derived from the model field's `help_text` value by default.
- `f.keywords` - Other related keywords (this is primarily applicable for search indexing)
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

### Data Properties

- `f.enumerable` - A flag denoting if the field's data is composed of an enumerable set. During a [init](avocado-init), each field's data is evaluated based on the internal type and the size of the data (number of distinct values). By default, if the field is a `CharField` and has `ENUMERABLE_MAXIMUM` or less distinct values, this will be set to `True`.

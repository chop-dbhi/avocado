---
layout: page
title: "Managing Your Metadata"
category: guide
date: 2013-03-02 08:38:03
---

One of the challenges of data model derived metadata is keeping it up-to-date when schema changes occur. Conveniently, there is library called [South](http://south.readthedocs.org) for Django which provides an API for creating schema and data migration scripts. If you aren't using this for your models, you should be. In fact, as of version 2.0.7, Avocado requires it as a hard dependency.

### Migration Command

_New in Avocado 2.0.15_

The migration command acts as an _all-or-nothing_ migration step for your project's metadata. Metadata in Avocado is both descriptive and functional. Therefore it is crucial to ensure metadata is properly up-to-date during a deployment to production (or any remote environment).

When the migration command is run, it performs these steps:

- Creates a fixture of `DataField`, `DataConcept`, `DataCategory`, and `DataConceptField` objects
- Creates a South data migration script that will load the fixture

The data migration script utilizes an internal function `avocado.core.backup.safe_load` which will:

- Create a backup fixture of the metadata from the target database
- Attempt to load the new fixture
- If the load fails, the backup will be re-loaded back into the database

For extra relief, this is all performed in a transaction (assuming the database supports transactions).

The migration command requires the `METADATA_MIGRATION_APP` setting be defined in the `AVOCADO` dict:

```python
AVOCADO = {
    'METADATA_MIGRATION_APP': 'someapp',
    ...
}
```

This is required so South knows where to manage the migrations as well as where the metadata fixtures should go. All fixtures created in this way will be versioned (like South migrations) with the number prefix, e.g. `0001_`.

**A word of caution**: this command creates a fixture with **all** metadata in the current database. This means if metadata has been created for models that are not yet in deployed, they will be problematic. A safe guard against this is to ensure the `DataField`s and `DataConcept`s are not marked as `published`.

A common workflow to prevent this from happening is doing this as the last step prior to a deployment. In future revisions of this command, additional checks may be put in place to validate all metadata prior to generating the fixture.

To run the command simply do:

```bash
$ python manage.py avocado migration
```

This will print out the details of what it's doing.

### Incremental/Fine-grain Control

Using South's `datamigration` command, keeping the Avocado metadata up-to-date is quite simple. After every schema migration is created, immediately create a data migration to update the metadata corresponding to the schema changes.

Here is an example. You add your first model to the `library` app:

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    pub_date = models.DateField()
    ...
```

You run the initial schema migration and sync your metadata:

```bash
python manage.py schemamigration library --initial
python manage.py migrate library
python manage.py avocado sync library
```

As a contrived example, you choose to rename `pub_date` to `published` because it looks nicer. Once you change the model, you create a new schema migration:

```bash
python manage.py schemamigration library --empty
```

The `forwards` method of the migration class will look something like this:

```python
def forwards(self, orm):
    db.rename_column('library_book', 'pub_date', 'published')
```

Create a data migration to update the corresponding `DataField`:

```bash
python manage.py datamigration library metadata_migration_for_0002
```

The `forwards` method of the migration class will look something like this:

```python
def forwards(self, orm):
    try:
        f = DataField.objects.get_by_natural_key('library.book.pub_date')
    except DataField.DoesNotExist:
        return
    f.field_name = 'published'
    f.save()
```

Now the migrations can be applied which will perform the schema migration and the data migration for the Avocado metadata:

```bash
python manage.py migrate library
```

> **NOTE:** Although the above example keeps the schema migration separate from the data migration for metadata, they can technically occur in the same script. This would involve adding the metadata-related migration logic in the schema migration script. The downside to this (and why it is not used in the example) is the lack of separate of concerns between [DDL](http://en.wikipedia.org/wiki/Data_definition_language) and [DML](http://en.wikipedia.org/wiki/Data_manipulation_language) statements. Also, from a coding standpoint, it is more clear and maintainable to keep the scripts separate. The only minor downside to the above approach is that the two migrations must occur in succession to prevent metadata inconsistencies.

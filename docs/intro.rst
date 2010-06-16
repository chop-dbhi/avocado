Introduction
============

Avocado is a flexible API providing metadata-driven database queries. It uses
the Django object-relational mapper (ORM) to dynamically construct queries,
without explicitly building a QuerySet object. Let's learn by example::

    # myapp/models.py
    
    class BlogEntry(models.Model):
        author = models.ForeignKey(User)
        title = models.CharField(max_length=100)
        tags = models.ManyToManyField(Tag)
        created = models.DateField(auto_add=True)
        modified = models.DateField(auto_add_now=True)
    
    
    class Tag(models.Model):
        name = models.CharField(max_length=20)


Defined are two models and they have a relationship via ``tags``. The
``BlogEntry`` model also has a reference to ``django.contrib.auth.models.User``.
The first requirement of ``avocado`` is to build an index of your models --
this is the metadata part. ::

    $ ./manage.py syncdb
    $ ./manage.py buildfieldindex myapp

The command ``buildfieldindex`` introspects all the models within ``myapp``
and stores off a small amount of metadata about each non-relational field on
each model. Programmatically, one could do this::

    >>> from avocado.models import FieldConcept
    >>> fc = FieldConcept(name='Entry Title', field_name='title',
    ...     model_label='myapp.blogentry')
    ...
    >>> fc.save()

    >>> fc.model
    <class 'myapp.models.BlogEntry'>

    >>> fc.field, fc.field.name
    (<django.db.models.fields.CharField object 0x1015a6850>, 'title')

As one can see, the minimum amount of metadata required is a name, the
reference to the app and model from where is came, and the name of the field
relative to the model. By building this index, you are virtually creating a
unique identifier that is associated with a single component of your data
model.

The two attributes shown above, ``fc.model`` and ``fc.field``, point to the model class and the instance of the field this metadata represents, respectively.
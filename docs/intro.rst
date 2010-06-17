Introduction
============

Avocado is a metadata-driven approach to building queries and reporting data.
It works with the Django object-relational mapper (ORM) to dynamically
construct queries, but without needing to explicitly define the relationships
between models. Here is a typical example of "explicitly defining
relationships"::

    User.objects.filter(entries__tags__name='python',
        entries__title__icontains='django')

The question is, "which users have blog entries containing the word
``django`` that also have the tag ``python``?" That is a perfectly valid
question to ask. The issue comes, when you want to change the question. A
question is defined with certains variables, but the context of the question
will always remain the same.

To take it one step farther, not only do not need to specify relationships
between models, you don't even need to know which objects you want to return
ahead of time, i.e. ``User`` vs. ``Tag``.

A Convoluted Example
--------------------
::

    # myapp/models.py
    
    class BlogEntry(models.Model):
        author = models.ForeignKey(User, related_name='entries')
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

As one can see, the minimum amount of metadata required is a name, a string
``app.model``, representing the app and model, and the name of the field
relative to the model. By building this index, you are virtually creating a
unique identifier that is associated with a single component of your data
model. Let us explore a few helpful attributes. ::

    >>> fc.model
    <class 'myapp.models.BlogEntry'>

    >>> fc.field, fc.field.name
    (<django.db.models.fields.CharField object 0x1015a6850>, 'title')


The two attributes shown above, ``fc.model`` and ``fc.field``, point to the
model class and the instance of the field this metadata represents,
respectively. To prove this::

    >>> fc.model is BlogEntry
    True

    >>> title_field = BlogEntry._meta.get_field_by_name('title')[0]
    >>> fc.field is title_field
    True

What we have above is all the necessary metadata we need for dynamic queries.
If you were paying attention you should be asking "but where are the
relationships!" So the above piece provides the means of storing off metadata
about our data model. Here is the second piece::

    >>> from avocado.modeltree import ModelTree

This is more or less the brains behind building dynamic queries. We start out
by specifying a model we want to build the query from. There are of course
dynamic and generic means of doing this (``django.db.models.get_model``), but
for simplicity sake, we are going to explicitly set ours to ``User``. ::

    >>> from django.contrib.auth.models import User
    >>> mt = ModelTree(User)

Now for the cool part. ::

    >>> mt.print_path()
    "User" at a depth of 0
    - - "Group" at a depth of 1
    - - "Permission" at a depth of 1
    - - - - "ContenType" at a depth of 2
    - - "Message" at a depth of 1
    - - "BlogEntry" at a depth of 1
    - - - - "Tag" at a depth of 2

So what is this you ask? This displays the full hierarchy of relationships
starting from a top level model ``User``. Each model relationship is recursively
traversed and a tree is built up of ``ModelTreeNode`` objects. ``mt.root_node``
is the node associated with the ``User`` model. All nodes have a list of
``children`` and a ``parent`` node.

So where are these dynamic queries? ::

    >>> path = mt.path_to(Tag)
    >>> query_rel = '__'.join(mt.query_string_path(path))
    >>> query_rel
    'entries__tags'

Having built this "relationship tree" we can now traverse any path and determine
the query string (or sequence of accessor names) necessary to get to a model.
This leaves the last bit of tacking on the actual field of interest::

    >>> kwargs = {'__'.join([query_rel, 'name')]: 'python'}
    >>> User.objects.filter(**kwargs)


Outro
-----

To bring this example together, we have two components: (1) an index of your
data model via a unique identifier, and (2) a means of dynamically determining
relationships between models. Using these two things together allows for some
pretty interesting methods of building queries, since at a very minimum you
need:

    - the ``id`` of the FieldConcept object of interest, e.g. ``Tag.name``
    - a condition, e.g. "python" for ``Tag.name``
    - the model the query is relative to, e.g. ``User``

This turns out to be like::

    >>> fc = FieldConcept.objects.get(id=4) # hypothetically
    >>> fc.name
    'Tag Name'

    >>> mt = ModelTree(User)
    >>> path = mt.path_to(fc.model)
    >>> kwarg = {'__'.join(path + fc.field_name): 'python'}

    >>> users = User.objects.filter(**kwargs)

This is the dynamic equivalent to doing::

    >>> users = User.objects.filter(entries__tags__name='python')

The power of this approach cannot be seen in this simple convoluted example,
but rather in data models that are large and in situtations in which you might
not know what kind questions about the data are going to be asked.


The Data Model Index
====================

``avocado.models.Field`` provides the structure to create an index of your
project's data model. ``Field`` has three required fields that provide the
unique identifier to a particular data model field, ``app_name``,
``model_name``, and ``field_name``. The ``app_name`` is the unique identifier
with respect to a Django project since a project cannot reference two apps of
the same name (this may change in later versions of Django). Therefore,
``app_name.model_name.field_name`` acts as an "absolute path" (or `natural key`_)
to a field in your data model. By building this meta index, each field can be
uniquely referenced by the above or by the database row's primary key.

.. _`natural key`: http://en.wikipedia.org/wiki/Natural_key

The recommended way to build the index initially is to use the
``build_model_index`` command supplied with avocado. One thing to note is that
``build_model_index`` does not add fields that are identifiers (e.g. AutoField,
ForeignKey). The reason is that in most cases it is unnecessary or otherwise
does not make sense to index those fields (of course there are uses of
indexing primary keys for determining unique counts of particular tables,
more on this later).

.. note::
   By default, categories corresponding to the models will be created and the
   respective fields will be added to each category (this can be turned off by
   supplying the ``--no--categories`` flag).

.. seealso::
   :doc:`modelfield`


Relationships Don't *Have* to Matter
------------------------------------

As mentioned above, relationships are not indexed by default. The ``ModelTree``
class, instead, handles determining relationships between models. Used in
combination with the ``ModeField`` index, dynamic queries can be created with
very little effort.

``ModelTree`` recursively builds a "tree" of nodes that store off direct
relational information such as parent (where it came from) and child (where
it can go) relationships. All ``ModelTree`` objects are derived from a "root
model", which acts as a starting point for traversing the relationships. If it
is desirable to have multiple starting points, multiple ``ModelTree`` objects
can be created with different root models.

Finding a path to another model is simple. You call the method ``path_to`` on
the ``ModelTree`` object and provide it a model class. This will determine the
shortest path to the model and will  return a node path. There are many ways
to utilize the node path, but the query string representation is the most common
of interest. Simply call the ``query_string`` method and pass in the nodes. This
is equivalent to writing out a query string (the key portion) for use in a
filter.


A Contrived Example
-------------------

Given the models ``Parent``, ``Child``, and ``Toy``, one could ask the question
"which parents have children who have toys that are Legos?" Traditionally, one
would have to write::

    >>> Parent.objects.filter(children__toys__name="Legos")

Using the ``ModelTree`` method::

    >>> from avocado.modeltree import ModelTree

    >>> mt = ModelTree(Parent)
    >>> path = mt.path_to(Toy)
    >>> key = mt.query_string(path, field_name="name")
    >>> key
    'children__toys__name'

    >>> Parent.objects.filter(**{key: "Legos"})

The interesting thing here is that there is no mention of the ``Child`` model.
There is no reference to it, nothing that inferred it, or anything. The 
``ModelTree`` object determined that the connection between ``Parent`` and
``Toy`` is ``Child`` dynamically.


The ``M`` Class
---------------

To facilitate ease of use with respect to the ``Field`` index, the ``M``
class enables very simple "query by value" without needing to know the
field's origin (what model it is apart of).

Taking the above two examples to the next level of simplicity, one could do::

    Parent.objects.filter(M(name="Legos"))

Unlike the previous two examples, using the ``M`` class to specify a condition
doesn't even require knowing the end model (where the field "name" lives on).
Note that there are two assumptions made here. One being that there is one
``Field`` object that has a ``field_name`` of "name". If this is untrue,
an ``AmbiguousField`` exception will be thrown. One could also do this to be
less ambiguous::

    Parent.objects.filter(M(toy__name="Legos"))

The only difference between the two is that the model class name where "name"
lives is specified, i.e. "toy".

.. warning::
   Do not confuse this with the Django query string lookups. The earlier example
   specifies the *toys* relationship with respect to ``Child``. In this example,
   *toy* refers to the name of the model.

The second assumption is that the ``M.modeltree`` attribute is set to a 
``ModelTree`` object with a root model of ``Parent``. If not explicity set,
the ``DEFAULT_MODELTREE`` constant derived from the avocado setting
``MODELTREE_MODELS`` is used. It is not important to understand this setting
or it's utility at the moment, but for completeness the ``M`` uses this under
the hood. If a different ``ModelTree`` object is desirable (or to explicitly
define the ``ModelTree`` object), one could do::

    mt = ModelTree(Parent)
    Parent.objects.filter(M(mt, toy__name="Legos"))

The ``M`` constructor takes an optional keyword argument ``modeltree`` which
defines the ``ModelTree`` object to derive the relationships from.

.. note::
   If for the off-chance that a field in your data model is also called
   "modeltree", simply pass ``ModelTree`` object as the first positional
   argument or set the attribute before using it::

       >>> M.modeltree = ModelTree(Parent)
       >>> Parent.objects.filter(M(toy__name="Legos"))
   
   Do note though, that for the duration of the ``M`` class' use within the
   namespace in which it was imported, the new ``M.modeltree`` object will
   persist.

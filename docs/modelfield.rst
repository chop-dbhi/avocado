The ``ModelField`` API
======================

As discussed in the :doc:`intro`, the ``ModelField`` model class provides
a means of creating an index of your data model. Of course, metadata can only be
as useful as how well it defines the data model. That is, the less ambigious the
definition of one's data model, the more accurately it can be represented. A few
helper methods and attributes have been built-in to ``ModelField`` class to
faciliate honing in on this definition.


The Basics
----------

Since a ``ModelField`` object actually represents a field on one of your models,
there a few properties that refer to it::

    >>> mf = ModelField(app_name='myapp', model_name='toy', field_name='name')
    >>> mf.model
    <class 'myapp.models.Toy'>

    >>> mf.field
    <django.db.models.fields.CharField object at 0x1018a7650>

These represent the actually ``Toy`` model and the field on the ``Toy`` model
that represents ``name``, respectively.


Choices
-------

A ``ModelField`` object can be enabled to specify "choices", a set of values
that can be used for restricting what can be queried and/or for validation
purposes. ``choices`` can be activated by setting ``enable_choices`` to
``True``. By default, the ``chocies`` property will be populated by
introspection, with a ``SELECT DISINCT`` on the database column. To specify
a custom set of choices, ``choices_handler`` can be set. The three types of
custom handlers include:

- an attribute name that lives on the model class
- an attribute name that lives on the model class' module
- a python datastructure that can be evaluated

An example of the last one::

    >>> mf = ModelField()
    >>> mf.choices_handler = "[(1, 'One'), (2, 'Two')]"
    >>> mf.enable_choices = True
    >>> mf.choices
    [(1, 'One'), (2, 'Two')]

In this case, the ``choices_handler`` is simply evaluated to a native python
datastructure.

The handler must follow the Django forms structure, that is, a list of tuple
pairs containing the actual value and the human-readable value. This is to
facilitate Django form generation.

.. warning::
   For performance reasons, ``choices`` is a property which caches the choices
   the first time it is evaluated. Therefore if the data changes (introspection)
   or if the ``choices_handler`` is changed, all objects should call
   ``reset_choices()`` to ensure the latest choices.


Translators
-----------

It is common practice when designing query interfaces to *not* display all
possible options for building a query. In most cases, there are simply too
many ways to ask the same question or the question that is being asked is
too difficult to explicitly convey in the user interface. 

For this reason, a translator can be specified for ``ModelField`` objects.
Translators are singletons which are registered with the ``TranslatorLibrary``.
Each singleton, when called, takes an ``operator``, ``value`` and the
``ModelField`` object it is acting on. It returns a ``django.db.models.Q``
object for use with the django ORM.

.. seealso::
   :doc:`translators`

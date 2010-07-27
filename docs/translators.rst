The Translator API
===================

The concept behind the translator derived from the need to take simple user
input and be able to apply some conditional logic which determines the
native query condition.

Every translator subclasses ``avocado.fields.translators.AbstractTranslator``.
The two public methods of interest are ``validate`` and ``translate``. We will
get back to these later.


Operators
---------

In ``avocado.fields.operators`` lives the ``Operator`` class and all of the
subclass singletons. Currently, each singleton maps to one of the available
Django ``QuerySet`` lookup operators and has three attributes:

- ``operator`` - the Django operator it maps to, e.g. 'lte'
- ``short_name`` - a short, but human-readable name, e.g. '<='
- ``verbose_name`` - a verbose english name, e.g. 'is less than or equal to'

In addition, each singleton has an ``is_valid`` method which takes a value
the operator is going to be applied to, to ensure they are compatible::

    >>> from avocado.fields import operators as ops
    >>> ops.lte.is_valid(5)
    True

    >>> ops.inlist.is_valid([1, 2])
    True

    >>> ops.inlist.is_valid(1)
    False

The last test failed since the SQL ``IN`` clause requires an array of values
to test against.

.. note::
   Currently the singletons do not validate a value's type, e.g. the integer
   literal ``5`` will validate true with ``ops.iexact`` even though case-\
   insensitive lookups against non-strings are invalid in SQL without a type
   cast.

   The validation is currently only concerned with the datastructure. Type
   coercion happens via the Django ORM, therefore it is not a concern here.


Validation
----------

Having the ability to construct dynamic queries has many upsides, but without
minor precaution this can leave you with queries that are invalid or simply
don't make sense. Since the true complexity of the query is unknown until it is
fully constructed, it is important to incrementally validate the correctness of
each component of the query as it becomes available, i.e. don't wait till the
``QuerySet`` is fully constructed before testing if it is broken.

Validation pertaining to ``ModelField`` objects is important since they are the
root of this dynamic query engine. When evaluating whether a particular value
and operator are valid for use as a query condition, there are a few questions
to be asked:

**Does the value make sense for the field?**

At a very basic level, a check should be performed prior to building a query to
see if the value is appropriate for the field it is performing the query on. A
simple example is that a numeric field does not (cannot) accept a non-numeric
value.

**Is the value an available choice?**

If the ``ModelField`` object has ``enable_choices`` set to true, the value must
be one of the available choices.

**Does the operator make sense for the field?**

When constructing a query, it is important to ensure an operator is chosen that
makes sense for the field's datatype, e.g. the '<=' does not make sense for a
boolean datatype.

**Does the value make sense for the operator?**

Certain operators require more than one value specified, such as ``between``,
where it requires exactly two.



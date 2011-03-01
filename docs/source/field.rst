The ``Field`` API
======================

As discussed in the :doc:`intro`, the ``Field`` model class provides
a means of creating an index of your data model. Of course, metadata can only be
as useful as how well it defines the data model. That is, the less ambiguous the
definition of one's data model, the more accurately it can be represented. A few
helper methods and attributes have been built-in to ``Field`` class to
faciliate honing in on this definition.

The *fields* of ``Field``
-------------------------

app_name
~~~~~~~~
The name of the app this field's model resides.

model_name
~~~~~~~~~~
The name of the model this field represents.

field_name
~~~~~~~~~~
The name of field as defined on the model.

.. note::

    Collectively, the above three fields define a "natural key" for a field
    in your project's data model. In fact, it has natural key support for
    data serialization.

    More information here: `Natural keys`_

name
~~~~
A more readable or verbose name of the field.

is_public
~~~~~~~~~
A flag defining whether or not the field is available to be used by clients.

summary (optional)
~~~~~~~~~~~~~~~~~~
A short summary of what the field means or represents.

description (optional)
~~~~~~~~~~~~~~~~~~~~~~
A full description of what the field means or represents.

keywords (optional)
~~~~~~~~~~~~~~~~~~~
Additional keywords not used in the ``summary`` or ``description`` that will
improve full-text searches.

group (optional)
~~~~~~~~~~~~~~~~
A group (``django.contrib.auth.models.Group``) to restrict access to only users
of this group.

sites (optional)
~~~~~~~~~~~~~~~~
One or more sites (``django.contrib.sites.models.Site``) this field is
available on.

status (optional)
~~~~~~~~~~~~~~~~~
A "review" status of the field for basic triaging.

note (optional)
~~~~~~~~~~~~~~~
A "review" note to faciliate triaging of the field.

reviewed (optional)
~~~~~~~~~~~~~~~~~~~
The last "review" date.

translator (optional)
~~~~~~~~~~~~~~~~~~~~~
A translator to be used while processing conditions utilizing the field.
See also :doc:`translators`.

enable_choices
~~~~~~~~~~~~~~
A flag that constrains the values that can be queried as well as used for
condition validation. By default, the choices are determined by data
introspection i.e. a ``SELECT DISTINCT`` query performed on the field.

Default: ``False``

.. _`Natural keys`: http://docs.djangoproject.com/en/dev/topics/serialization/#natural-keys

The Basics
----------

Since a ``Field`` object actually represents a field on one of your models,
there a few properties that refer to it::

    >>> field = Field(app_name='myapp', model_name='toy', field_name='name')
    >>> field.model
    <class 'myapp.models.Toy'>

    >>> field.field
    <django.db.models.fields.CharField object at 0x1018a7650>

These represent the actually ``Toy`` model and the field on the ``Toy`` model
that represents ``name``, respectively.

The high-level datatype of the field is defined as a property::

    >>> field.datatype
    'string'

This can be useful for clients that may need to know what values the field
can accept.

Want to see a list of distinct values for this field? Use the 
``values`` property::

    >>> field.values
    ('Legos', 'Erector Set', 'Silly Putty')

.. warning::

    For certain fields, it may not be wise to get a distinct list of values
    since the list may be very large, specifically for large text fields or
    numerical data.

A distinct list of values may be useful for clients, but to better understand
the underlying data, a distribution of the values can be more useful::

    >>> field.distribution()
    [(35, 'Legos'), (10, 'Silly Putty'), (2, 'Erector Set')]



Introduction
============

Avocado is a metadata-driven query engine which utilizes Django's Object-
Relational Mapping (ORM) to construct queries at runtime. It was developed
within a research environment for secondary use of clinical data, where data
*discovery* is important for understanding the quality and contents of the
data.

.. note::

    Although it was built from within a clinical research environment, Avocado
    has been written in a generic fashion which lends itself to be used across
    various domains.

    For the remainder of the documentation, examples will be explained in the
    context of clinical research since it is an great application for Avocado.

The Basics
----------
Avocado acts as a metadata layer for Django models. There is quite a bit of
metadata that can be derived from the model itself, but Avocado provides means
for adding additional metadata to models.

A Django model is simply a container for *fields* which corresponds to a database
table column, ultimately where the data itself is stored. Avocado *indexes*
fields intended to be exposed for query purposes.

The goal of Avocado is to increase and improve the accessibility of the data
represented by these indexed fields.

As an example, we have a simple (contrived) model::

    class Patient(models.Model):
        first_name = models.CharField(max_length=30)
        middle_name = models.CharField(null=True)
        last_name = models.CharField(max_length=30)
        dob = models.DateField()
        ...

We can derive a few pieces of metadata from these fields that can be used
to inform end-users *how* to query this patient model. For example, the date of
birth field (``dob``) is of the type *date*, therefore it constrains the
variability of the query conditions which increase the reliability of the query
results. We are using the database schema to our advantage.
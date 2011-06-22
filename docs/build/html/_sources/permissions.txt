Authorization
=============

Coming from a clinical research environment, there are two slightly different
audiences when it comes to exposing access to certain data. There are, of course,
the researchers whom are interested in the data at an aggregate level and there
are the clinicians who, in addition, have an interest in using the data for
operational use. The challenge is being able to reuse the overlapping definitions
and only make available the operational-specific definitions to clinicians.

To solve this probelm Avocado comes integrated with Django's `"sites" framework`_
for site-wide authorization as well as the `django-guardian`_ library for
object-level permissions.

Site-Wide
---------
Using Django's `"sites" framework`_, access to certain definitions can be restricted
on a per-site basis. For our needs, we had an internal deployment (behind the
firewall) of our application which made available operational data not allowed
on our external deployment (accessible from the Internet).

Since the ``Definition`` model is the "closest to the data", permissions are
applied here. A definition can be associated to one or more sites.

::

    ...
    >>> definition.sites.add(site1)     # now accessible by site1
    >>> definition.sites.add(site2)     # now accessible by site2
    >>> definition.sites.clear()        # not accessible by any site
    ...

Groups and Users
----------------
In our environment, users have varying roles depending on their research
requirements. Certain users are only allowed to have access to certain data,
therefore we needed to created groups which inferred a level of authorization.

Here we use Django's ``Group`` model from the `"auth" framework` to enable
access of definitions to groups.

::

    ...
    >>> definition.groups.add(group1)   # now accessible by group1
    >>> definition.groups.add(group2)   # now accessible by group2
    >>> definition.groups.clear()       # not accessible by any group
    ...

If needed, specific users can be granted/revoked access to certain definitions.

::

    ...
    >>> definition.users.add(user1)     # now accessible by user1
    >>> definition.users.add(user2)     # now accessible by user2
    >>> definition.users.clear()        # not accessible by any user
    ...


.. _`"sites" framework`: http://docs.djangoproject.com/en/dev/ref/contrib/sites/
.. _`django-guardian`: http://pypi.python.org/pypi/django-guardian
.. _`"auth" framework`: http://docs.djangoproject.com/en/dev/topics/auth/

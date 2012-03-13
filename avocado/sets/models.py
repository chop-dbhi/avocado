from datetime import datetime
from django.db import models
from store.models import Descriptor, Scope

class ObjectSet(Descriptor):
    """
    Provides a means of saving off a set of objects.

    `criteria' is persisted so the original can be rebuilt. `removed_ids'
    is persisted to know which objects have been excluded explicitly from the
    set. This could be useful when testing for if there are new objects
    available when additional data has been loaded, while still excluding
    the removed objects.

    `ObjectSet' must be subclassed to add the many-to-many relationship
    to the "object" of interest.
    """
    scope = models.OneToOneField(Scope, editable=False)
    count = models.PositiveIntegerField(null=True, editable=False, db_column='cnt')

    class Meta(object):
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.now()
        self.modified = datetime.now()
        super(ObjectSet, self).save(*args, **kwargs)


class ObjectSetJoinThrough(models.Model):
    """
    Adds additional information about the objects that have been ``added`` and
    ``removed`` from the original set.

    For instance, additional objects that are added which do not match the
    conditions currently associated with the ``ObjectSet`` should be flagged
    as ``added``. If in the future they match the conditions, the flag can be
    removed.

    Any objects that are removed from the set should be marked as ``removed``
    even if they were added at one time. This is too keep track of the objects
    that have been explicitly removed from the set.
    """
    removed = models.BooleanField(default=False)
    added = models.BooleanField(default=False)

    class Meta(object):
        abstract = True




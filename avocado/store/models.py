from django.db import models, transaction, connections
from django.contrib.auth.models import User

from avocado.db_fields import PickledObjectField

__all__ = ('Scope', 'Perspective', 'Report')

class Descriptor(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)    

    class Meta:
        abstract = True
        app_label = 'avocado'


class Context(Descriptor):
    """A generic interface for storing an arbitrary context around the data
    model. The object defining the context must be serializable.
    """
    store = PickledObjectField()
    definition = models.TextField(editable=False)

    class Meta:
        abstract = True
        app_label = 'avocado'

    def define(self):
        "Interprets the stored data structure."
        raise NotImplementedError

    def write(self, obj):
        "Takes an object and writes it to the ``store``."
        self.store = obj

    def read(self):
        "Reads the ``store`` and returns an object."
        return self.store


class Scope(Context):
    "Stores information needed to provide scope to data."
    pass


class Perspective(Context):
    "Stores information needed to represent data."
    pass


class Report(Descriptor):
    "Represents a combination ``scope`` and ``perspective``."
    scope = models.ForeignKey(Scope)
    perspective = models.ForeignKey(Perspective)


class ObjectSet(Descriptor):
    """Provides a means of saving off a set of objects.

    `criteria' is persisted so the original can be rebuilt. `removed_ids'
    is persisted to know which objects have been excluded explicitly from the
    set. This could be useful when testing for if there are new objects
    available when additional data has been loaded, while still excluding
    the removed objects.

    `ObjectSet' must be subclassed to add the many-to-many relationship
    to the "object" of interest.
    """
    scope = models.ForeignKey(Scope)    
    cnt = models.PositiveIntegerField('count', editable=False)  
        
    class Meta:
        abstract = True

    def bulk_insert(self, object_ids, join_table, fk1, fk2):
        "Uses the SQL COPY command to populate the M2M join table."
        from cStringIO import StringIO

        cursor = connections['default'].cursor()

        buff = StringIO()

        for oid in object_ids:
            buff.write('%s\t%s\n' % (self.id, oid))
        buff.seek(0)

        cursor.copy_from(buff, join_table, columns=(fk1, fk2))

        transaction.set_dirty()
        transaction.commit_unless_managed()
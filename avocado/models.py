from django.db import models
from django.db.models.signals import post_syncdb
from django.db import connections, transaction

from avocado.concepts.models import *
from avocado.fields.models import *
from avocado.columns.models import *
from avocado.criteria.models import *

from avocado import signals

class ObjectSet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    cnt = models.PositiveIntegerField('count', null=True, blank=True)
    sql = models.TextField('initial SQL', null=True, blank=True)
    criteria = models.TextField(null=True, blank=True)
    added_ids = models.TextField(null=True, blank=True)    
    removed_ids = models.TextField(null=True, blank=True)
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return u'%s' % self.name

    def bulk_insert(self, object_ids, join_table, fk1, fk2):
        "Uses the SQL COPY command to populate the M2M join table."
        from cStringIO import StringIO

        cursor = connections['default'].cursor()
        
        buff = StringIO()

        for oid in objects_ids:
            buff.write('%s\t%s\n' % (self.id, oid))
        buff.seek(0)

        cursor.copy_from(buff, join_table, columns=(fk1, fk2))
        
        transaction.set_dirty()
        transaction.commit_unless_managed()    


post_syncdb.connect(signals.load_custom_sql)

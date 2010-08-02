import base64

from django.db import models, connections, transaction
from django.contrib.auth.models import User

from avocado.db_fields import PickledObjectField
from avocado.columns.models import Column
from avocado.columns import utils
from avocado.fields import logictree

__all__ = ('DynamicQuery', 'ObjectSet')

class QueryDescriptor(models.Model):
    "Contains a set of fields that can be used to describe a particular query."
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    cnt = models.PositiveIntegerField('count', null=True, blank=True)
    
    class Meta:
        abstract = True


class ObjectSet(QueryDescriptor):
    """Provides a means of saving off a set of objects.

    `criteria' is persisted so the original can be rebuilt. `removed_ids'
    is persisted to know which objects have been excluded explicitly from the
    set. This could be useful when testing for if there are new objects
    available when additional data has been loaded, while still excluding
    the removed objects.

    `ObjectSet' must be subclassed to add the many-to-many relationship
    to the "object" of interest.
    """
    criteria = PickledObjectField()
    removed_ids = PickledObjectField()

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


def _encode_url(value):
    return base64.urlsafe_base64encode(str(value))

def _decode_url(self, url):
    return base64.urlsafe_base64decode(url)

class DynamicQuery(QueryDescriptor):
    """Provides a means of saving off a dynamic query by serializing each main
    component to a stringified JSON format. On retrieval, the query is
    regenerated. As new data is loaded or updated, those data will be reflected
    in dynamic queries.
    """
    criteria = PickledObjectField()
    columns = PickledObjectField()
    ordering = PickledObjectField()

    sql = models.TextField('SQL representation', null=True, blank=True,
        help_text='A snapshot of the last saved query')
    
    class Meta:
        app_label = u'avocado'

    def store_sql(self, queryset):
        queryset.query.clear_limits()
        self.sql = str(queryset.query)
    
    def q(self, modeltree):
        node = logictree.transform(modeltree, self.criteria)
        return node.q
    
    def generate(self, modeltree=None):
        if modeltree is None:
            from avocado.modeltree import DEFAULT_MODELTREE
            modeltree = DEFAULT_MODELTREE

        queryset = modeltree.root_model.objects.all()
        
        # apply criteria
        if self.criteria:
            queryset = queryset.filter(self.q(modeltree))
        
        if self.columns or self.ordering:
            if self.columns:
                queryset = utils.add_columns(queryset, self.columns, modeltree)
            if self.ordering:
                queryset = cset.add_ordering(queryset, self.ordering, modeltree)
        
        return queryset
    
    def get_url(self):
        if self.id is not None:
            return _encode_url(self.id)
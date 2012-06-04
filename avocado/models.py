import jsonfield
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode
from django.db.models.fields import FieldDoesNotExist
from django.db.models.signals import post_save, pre_delete
from django.core.exceptions import ImproperlyConfigured
from avocado.core import utils
from avocado.core.models import Base, BasePlural
from avocado.core.cache import post_save_cache, pre_delete_uncache, cached_property
from avocado.conf import OPTIONAL_DEPS, settings as _settings
from avocado.managers import DataFieldManager, DataConceptManager, DataCategoryManager
from avocado.query import parsers
from avocado.query.translators import registry as translators
from avocado.query.operators import registry as operators
from avocado.stats.agg import Aggregator
from avocado.dataviews.formatters import registry as formatters
from avocado.dataviews.queryview import registry as queryviews

__all__ = ('DataCategory', 'DataConcept', 'DataField', 'DataContext')

INTERNAL_DATATYPE_MAP = _settings.INTERNAL_DATATYPE_MAP
DATA_CHOICES_MAP = _settings.DATA_CHOICES_MAP


class DataCategory(Base):
    "A high-level organization for data concepts."
    # A reference to a parent for hierarchical categories
    parent = models.ForeignKey('self', null=True, blank=True,
        related_name='children')
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = DataCategoryManager()

    class Meta(object):
        ordering = ('order', 'name')
        verbose_name_plural = 'data categories'


class DataField(BasePlural):
    """Describes the significance and/or meaning behind some data. In addition,
    it defines the natural key of the Django field that represents the location
    of that data e.g. ``library.book.title``.
    """
    app_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    field_name = models.CharField(max_length=50)

    # An optional unit for this field's data. In some cases databases may have
    # a separate column which denotes the unit for another column, but this is
    # not always the case. Measurement data, for example, should be
    # standardized in the database to allow for consistent querying, thus not
    # requiring a separate column denoting the unit per value.
    unit = models.CharField(max_length=30, null=True, blank=True)
    unit_plural = models.CharField(max_length=40, null=True, blank=True)

    # Although a category does not technically need to be defined, this is more
    # for workflow reasons than for when the concept is published. Automated
    # prcesses may create concepts on the fly, but not know which category they
    # should be linked to initially.
    category = models.ForeignKey(DataCategory, null=True, blank=True)

    # Set this field to true to make this field's values enumerable. This should
    # only be enabled for data that contains a discrete vocabulary, i.e.
    # no full text data, most numerical data nor date or time data.
    enumerable = models.BooleanField(default=False)

    # Set his field to true to denote this field may be searched via some means
    # of free-text input.
    searchable = models.BooleanField(default=False)

    # An optional translator which customizes input query conditions
    # to a format which is suitable for the database.
    translator = models.CharField(max_length=100, blank=True, null=True,
        choices=translators.choices)

    # The timestamp of the last time the underlying data for this field
    # has been modified. This is used for the cache key and for general
    # reference. The underlying table may not have a timestamp nor is it
    # optimal to have to query the data for the max `modified` time.
    data_modified = models.DateTimeField(null=True, help_text='The last time ' \
        ' the underlying data for this field was modified.')

    # Enables recording where this particular data comes if derived from
    # another data source.
    data_source = models.CharField(max_length=250, null=True, blank=True)

    # Certain concepts may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    if OPTIONAL_DEPS['django.contrib.sites']:
        sites = models.ManyToManyField(Site, blank=True,
            related_name='fields+')

    # The order of this datafield with respect to the category (if defined).
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = DataFieldManager()

    class Meta(object):
        unique_together = ('app_name', 'model_name', 'field_name')
        ordering = ('name',)
        permissions = (
            ('view_datafield', 'Can view datafield'),
        )

    def __unicode__(self):
        if self.name:
            return u'{0} [{1}]'.format(self.name, self.model_name)
        return u'.'.join([self.app_name, self.model_name, self.field_name])

    # The natural key should be used any time fields are being exported
    # for integration in another system. It makes it trivial to map to new
    # data models since there are discrete parts (as suppose to using the
    # primary key).
    def natural_key(self):
        return self.app_name, self.model_name, self.field_name

    # Django Model Field-related Properties and Methods

    @property
    def model(self):
        "Returns the model class this field is associated with."
        if not hasattr(self, '_model'):
            self._model = models.get_model(self.app_name, self.model_name)
        return self._model

    @property
    def field(self):
        "Returns the field object this field represents."
        try:
            return self.model._meta.get_field_by_name(self.field_name)[0]
        except FieldDoesNotExist:
            pass

    @property
    def datatype(self):
        """Returns the datatype of the field this datafield represents.

        By default, it will use the field's internal type, but can be
        overridden by the ``INTERNAL_DATATYPE_MAP`` setting.
        """
        datatype = utils.get_internal_type(self.field)
        # if a mapping exists, replace the datatype
        return INTERNAL_DATATYPE_MAP.get(datatype, datatype)


    # Convenience Methods
    # Easier access to the underlying data for this data field

    def query(self):
        "Returns a `ValuesListQuerySet` for this data field."
        return self.model.objects.values(self.field_name)

    def search_values(self, query):
        "Rudimentary search for string-based values."
        if self.datatype == 'string':
            filters = {'{}__icontains'.format(self.field_name): query}
            return self.query().filter(**filters).values_list(self.field_name,
                flat=True).iterator()

    def get_plural_unit(self):
        if self.unit_plural:
            plural = self.unit_plural
        elif self.unit and not self.unit.endswith('s'):
            plural = self.unit + 's'
        else:
            plural = self.unit
        return plural

    # Data-related Cached Properties
    # These may be cached until the underlying data changes
    # TODO add maximum data size restriction

    @cached_property('size', timestamp='data_modified')
    def size(self):
        "Returns the size of distinct values."
        return self.query().distinct().count()

    @cached_property('values', timestamp='data_modified')
    def values(self):
        "Introspects the data and returns a distinct list of the values."
        return tuple(self.query().order_by(self.field_name)\
                .values_list(self.field_name, flat=True)\
                .order_by(self.field_name).distinct())

    @cached_property('coded_values', timestamp='data_modified')
    def coded_values(self):
        "Returns a distinct set of coded values for this field"
        if 'avocado.coded' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured('For this feature, avocado.coded app '
                    'must be added to INSTALLED_APPS')
        from avocado.coded.models import CodedValue
        return zip(CodedValue.objects.filter(field=self).values_list('value', 'coded'))

    @property
    def mapped_values(self):
        "Maps the raw `values` relative to `DATA_CHOICES_MAP`."
        # Iterate over each value and attempt to get the mapped choice
        # other fallback to the value itself
        return map(lambda x: smart_unicode(DATA_CHOICES_MAP.get(x, x)), self.values)

    @property
    def choices(self):
        "Returns a distinct set of choices for this field."
        return zip(self.values, self.mapped_values)

    # Data Aggregation Properties
    def groupby(self, *args):
        return Aggregator(self.field).groupby(*args)

    def count(self, *args):
        "Returns an the aggregated counts."
        return Aggregator(self.field).count(*args)

    def max(self, *args):
        "Returns the maximum value."
        return Aggregator(self.field).max(*args)

    def min(self, *args):
        "Returns the minimum value."
        return Aggregator(self.field).min(*args)

    def avg(self, *args):
        "Returns the average value. Only applies to quantitative data."
        return Aggregator(self.field).avg(*args)

    def sum(self, *args):
        "Returns the sum of values. Only applies to quantitative data."
        if self.datatype == 'number':
            return Aggregator(self.field).sum(*args)

    def stddev(self, *args):
        "Returns the standard deviation. Only applies to quantitative data."
        if self.datatype == 'number':
            return Aggregator(self.field).stddev(*args)

    def variance(self, *args):
        "Returns the variance. Only applies to quantitative data."
        if self.datatype == 'number':
            return Aggregator(self.field).variance(*args)

    # Translator Convenience Methods

    @property
    def operators(self):
        "Returns the valid operators for this datafield."
        trans = translators[self.translator]
        return tuple(trans.get_operators(self))

    @property
    def operator_choices(self):
        return [(x, operators[x].verbose_name) for x in self.operators]

    def translate(self, operator=None, value=None, tree=None, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.translate(self, operator, value, tree, **context)

    def validate(self, operator=None, value=None, tree=None, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.validate(self, operator, value, tree, **context)


class DataConcept(BasePlural):
    """Our acceptance of an ontology is, I think, similar in principle to our
    acceptance of a scientific theory, say a system of physics; we adopt, at
    least insofar as we are reasonable, the simplest conceptual scheme into
    which the disordered fragments of raw experience can be fitted and arranged.

        -- Willard Van Orman Quine
    """
    # Although a category does not technically need to be defined, this more
    # for workflow reasons than for when the concept is published. Automated
    # prcesses may create concepts on the fly, but not know which category they
    # should be linked to initially. the admin interface enforces choosing a
    # category when the concept is published
    category = models.ForeignKey(DataCategory, null=True, blank=True)

    # The associated fields for this concept. fields can be
    # associated with multiple concepts, thus the M2M
    fields = models.ManyToManyField(DataField, through='DataConceptField',
            related_name='concepts')

    # Certain concepts may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    if OPTIONAL_DEPS['django.contrib.sites']:
        sites = models.ManyToManyField(Site, blank=True,
            related_name='concepts+')

    order = models.FloatField(null=True, blank=True, db_column='_order')

    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields. If a formatter is not
    # defined, this DataConcept is not intended to be exposed since the
    # underlying data may not be appropriate for client consumption.
    formatter = models.CharField(max_length=100, blank=True, null=True,
        choices=formatters.choices)

    queryview = models.CharField(max_length=100, blank=True, null=True,
        choices=queryviews.choices)

    objects = DataConceptManager()

    class Meta(object):
        app_label = 'avocado'
        ordering = ('order',)
        permissions = (
            ('view_dataconcept', 'Can view dataconcept'),
        )


class DataConceptField(models.Model):
    "Through model between DataConcept and DataField relationships."
    field = models.ForeignKey(DataField, related_name='concept_fields')
    concept = models.ForeignKey(DataConcept, related_name='concept_fields')

    name = models.CharField(max_length=100, null=True, blank=True)
    name_plural = models.CharField(max_length=100, null=True, blank=True)
    order = models.FloatField(null=True, blank=True, db_column='_order')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('order',)

    def __unicode__(self):
        return unicode(self.name or self.field.name)

    def get_plural_name(self):
        return self.name_plural or self.field.get_plural_name()


class DataContext(Base):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    json = jsonfield.JSONField(null=True, blank=True,
        validators=[parsers.datacontext.validate])
    session = models.BooleanField(default=False)
    composite = models.BooleanField(default=False)

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True, related_name='datacontext+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def archive(self):
        if self.archived:
            return False
        backup = self.pk, self.session, self.archived
        self.pk, self.session, self.archived = None, False, True
        self.save()
        self.pk, self.session, self.archived = backup
        return True

    def _combine(self, other, operator):
        if not isinstance(other, self.__class__):
            raise TypeError('Other object must be a DataContext instance')
        cxt = self.__class__(composite=True)
        cxt.user_id = self.user_id or other.user_id
        if self.json and other.json:
            cxt.json = {
                'type': operator,
                'children': [
                    {'id': self.pk, 'composite': True},
                    {'id': other.pk, 'composite': True}
                ]
            }
        elif self.json:
            cxt.json = {'id': self.pk, 'composite': True}
        elif other.json:
            cxt.json = {'id': other.pk, 'composite': True}
        return cxt

    def __and__(self, other):
        return self._combine(other, 'and')

    def __or__(self, other):
        return self._combine(other, 'or')

    def apply(self, queryset=None, tree=None):
        "Applies this context to a QuerySet."
        if tree is None and queryset is not None:
            tree = queryset.model
        return parsers.datacontext.parse(self.json, tree=tree).apply(queryset=queryset)

    def language(self, tree=None):
        return parsers.datacontext.parse(self.json, tree=tree).language


# Register instance-level cache invalidation handlers
post_save.connect(post_save_cache, sender=DataField)
post_save.connect(post_save_cache, sender=DataConcept)
post_save.connect(post_save_cache, sender=DataCategory)

pre_delete.connect(pre_delete_uncache, sender=DataField)
pre_delete.connect(pre_delete_uncache, sender=DataConcept)
pre_delete.connect(pre_delete_uncache, sender=DataCategory)

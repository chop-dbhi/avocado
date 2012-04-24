try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django import forms
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import smart_unicode
from django.db.models.fields import FieldDoesNotExist
from django.db.models.signals import post_save, pre_delete
from django.core.exceptions import ImproperlyConfigured
from modeltree.tree import MODELTREE_DEFAULT_ALIAS, trees
from avocado.core import utils
from avocado.core.models import Base, BasePlural
from avocado.core.cache import post_save_cache, pre_delete_uncache, cached_property
from avocado.conf import settings as _settings
from avocado.managers import DataFieldManager, DataConceptManager, DataCategoryManager
from avocado.formatters import registry as formatters
from avocado.query.translators import registry as translators
from avocado.stats import Aggregator

__all__ = ('DataCategory', 'DataConcept', 'DataField')

SITES_APP_INSTALLED = 'django.contrib.sites' in settings.INSTALLED_APPS
INTERNAL_DATATYPE_MAP = _settings.INTERNAL_DATATYPE_MAP
DATA_CHOICES_MAP = _settings.DATA_CHOICES_MAP


class DataCategory(Base):
    "A high-level organization for data concepts."
    # A reference to a parent for hierarchical categories
    parent = models.ForeignKey('self', null=True, related_name='children',
            blank=True)

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

    # Although a category does not technically need to be defined, this more
    # for workflow reasons than for when the concept is published. Automated
    # prcesses may create concepts on the fly, but not know which category they
    # should be linked to initially. the admin interface enforces choosing a
    # category when the concept is published
    category = models.ForeignKey(DataCategory, null=True, blank=True)

    # Explicitly enable this field to be choice-based. This should
    # only be enabled for data that contains a discrete vocabulary, i.e.
    # no full text data, most numerical data nor date or time data.
    choices_allowed = models.BooleanField(default=False)

    # Explicitly allow or disallow sorting for this field. This can be used
    # to control expensive columns from being sorted.
    sorting_allowed = models.BooleanField(default=True)

    # An optional translator which customizes input query conditions
    # to a format which is suitable for the database.
    translator = models.CharField(max_length=100, choices=translators.choices,
        blank=True, null=True)

    # The timestamp of the last time the underlying data for this field
    # has been modified. This is used for the cache key and for general
    # reference. The underlying table not have a timestamp nor is it optimal
    # to have to query the data for the max `modified` time.
    data_modified = models.DateTimeField(null=True)

    # Enables recording where this particular data comes if derived from
    # another data source.
    data_source = models.CharField(max_length=250, null=True, blank=True)

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

        By default, it will use the field's internal type, but can be overridden
        by the ``INTERNAL_DATATYPE_MAP`` setting.
        """
        datatype = utils.get_internal_type(self.field)
        # if a mapping exists, replace the datatype
        return INTERNAL_DATATYPE_MAP.get(datatype, datatype)


    # Convenience Methods
    # Easier access to the underlying data for this data field

    def query(self):
        "Returns a `ValuesListQuerySet` for this data field."
        return self.model.objects.values(self.field_name)


    # Data-related Cached Properties
    # These may be cached until the underlying data changes

    @cached_property('size', timestamp='data_modified')
    def size(self):
        "Returns the size of distinct values."
        return self.query().distinct().count()

    @cached_property('values', timestamp='data_modified')
    def values(self):
        "Introspects the data and returns a distinct list of the values."
        return self.query().order_by(self.field_name)\
                .values_list(self.field_name, flat=True).distinct()

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


    # Validation and Query-related Methods

    def query_string(self, operator=None, tree=MODELTREE_DEFAULT_ALIAS):
        return trees[tree].query_string_for_field(self.field, operator)

    def translate(self, operator=None, value=None, tree=MODELTREE_DEFAULT_ALIAS, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.translate(self, operator, value, tree, **context)

    def validate(self, operator=None, value=None, tree=MODELTREE_DEFAULT_ALIAS, **context):
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
    if SITES_APP_INSTALLED:
        sites = models.ManyToManyField(Site, blank=True,
            related_name='concepts+')

    order = models.FloatField(null=True, blank=True, db_column='_order')

    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields. If a formatter is not
    # defined, this DataConcept is not intended to be exposed since the
    # underlying data may not be appropriate for client consumption.
    formatter = models.CharField(max_length=100, blank=True, null=True,
        choices=formatters.choices)

    objects = DataConceptManager()

    class Meta(object):
        app_label = 'avocado'
        ordering = ('order',)
        permissions = (
            ('view_dataconcept', 'Can view dataconcept'),
        )

    def __len__(self):
        return self.fields.count()


class DataConceptField(BasePlural):
    "Through model between DataConcept and DataField relationships."
    field = models.ForeignKey(DataField, related_name='concept_fields')
    concept = models.ForeignKey(DataConcept, related_name='concept_fields')
    order = models.FloatField(null=True, db_column='_order')

    class Meta(object):
        ordering = ('order',)

    def __unicode__(self):
        return unicode(self.name or self.field.name)

    def get_plural_name(self):
        return self.name_plural or self.field.get_plural_name()


# Register instance-level cache invalidation handlers
post_save.connect(post_save_cache, sender=DataField)
post_save.connect(post_save_cache, sender=DataConcept)
post_save.connect(post_save_cache, sender=DataCategory)

pre_delete.connect(pre_delete_uncache, sender=DataField)
pre_delete.connect(pre_delete_uncache, sender=DataConcept)
pre_delete.connect(pre_delete_uncache, sender=DataCategory)

# If django-reversion is installed, register the models
if 'reversion' in settings.INSTALLED_APPS:
    import reversion
    reversion.register(DataField)
    reversion.reversion(DataConceptField)
    reversion.register(DataConcept, follow=['concept_fields'])
    reversion.register(DataCategory)

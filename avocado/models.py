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
from modeltree.tree import MODELTREE_DEFAULT_ALIAS, trees
from avocado.core import binning, utils
from avocado.core.models import Base, BasePlural
from avocado.core.cache import post_save_cache, pre_delete_uncache, cached_property
from avocado.conf import settings as _settings
from avocado.managers import FieldManager, ConceptManager, CategoryManager
from avocado.formatters import registry as formatters
from avocado.query.translators import registry as translators

__all__ = ('Category', 'DataConcept', 'DataField')

SITES_APP_INSTALLED = 'django.contrib.sites' in settings.INSTALLED_APPS
INTERNAL_DATATYPE_MAP = _settings.INTERNAL_DATATYPE_MAP
DATA_CHOICES_MAP = _settings.DATA_CHOICES_MAP

class DataField(BasePlural):
    """Describes the significance and/or meaning behind some data. In addition,
    it defines the natural key of the Django field that represents the location
    of that data e.g. ``library.book.title``.
    """
    app_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    field_name = models.CharField(max_length=50)

    # Explicitly enable this field to be choice-based. This should
    # only be enabled for data that contains a discrete vocabulary, i.e.
    # no full text data, most numerical data nor date or time data.
    enable_choices = models.BooleanField(default=False)

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

    objects = FieldManager()

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

    # Data-related Cached Properties
    # These may be cached until the underlying data changes

    @cached_property('distribution', timestamp='data_modified')
    def distribution(self, *args, **kwargs):
        "Returns a binned distribution of this field's data."
        name = self.field_name
        queryset = self.model.objects.values(name)
        return binning.distribution(queryset, name, self.datatype, *args, **kwargs)

    @cached_property('values', timestamp='data_modified')
    def values(self):
        "Introspects the data and returns a distinct list of the values."
        if self.enable_choices:
            return self.model.objects.values_list(self.field_name,
                flat=True).order_by(self.field_name).distinct()

    @cached_property('coded_values', timestamp='data_modified')
    def coded_values(self):
        "Returns a distinct set of coded values for this field"
        if 'avocado.coded' in settings.INSTALLED_APPS:
            from avocado.coded.models import CodedValue
            if self.enable_choices:
                return zip(CodedValue.objects.filter(datafield=self).values_list('value', 'coded'))

    @property
    def mapped_values(self):
        "Maps the raw `values` relative to `DATA_CHOICES_MAP`."
        if self.enable_choices:
            # Iterate over each value and attempt to get the mapped choice
            # other fallback to the value itself
            return map(lambda x: smart_unicode(DATA_CHOICES_MAP.get(x, x)),
                self.values)

    @property
    def choices(self):
        "Returns a distinct set of choices for this field."
        if self.enable_choices:
            return zip(self.values, self.mapped_values)

    # Validation and Query-related Methods

    def query_string(self, operator=None, using=MODELTREE_DEFAULT_ALIAS):
        return trees[using].query_string_for_field(self.field, operator)

    def translate(self, operator=None, value=None, using=MODELTREE_DEFAULT_ALIAS, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.translate(self, operator, value, using, **context)

    def validate(self, operator=None, value=None, using=MODELTREE_DEFAULT_ALIAS, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.validate(self, operator, value, using, **context)


class Category(Base):
    "A high-level organization for concepts."
    # A reference to a parent Category for hierarchical categories.
    parent = models.ForeignKey('self', null=True, related_name='children')

    # Certain whole categories may not be relevant or appropriate for all
    # sites being deployed. If a category is not accessible by a certain site,
    # all subsequent data elements are also not accessible by the site.
    if SITES_APP_INSTALLED:
        sites = models.ManyToManyField(Site, blank=True, related_name='categories+')

    order = models.FloatField(null=True, db_column='_order')

    objects = CategoryManager()

    class Meta(object):
        ordering = ('order', 'name')


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
    category = models.ForeignKey(Category, null=True)

    # The associated fields for this concept. fields can be
    # associated with multiple concepts, thus the M2M
    fields = models.ManyToManyField(DataField, through='ConceptField')

    # Certain concepts may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    if SITES_APP_INSTALLED:
        sites = models.ManyToManyField(Site, blank=True, related_name='concepts+')

    order = models.FloatField(null=True, db_column='_order')

    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields. If a formatter is not
    # defined, this DataConcept is not intended to be exposed since the
    # underlying data may not be appropriate for client consumption.
    formatter = models.CharField(max_length=100, blank=True, null=True,
        choices=formatters.choices)

    objects = ConceptManager()

    class Meta(object):
        app_label = 'avocado'
        ordering = ('order',)
        permissions = (
            ('view_dataconcept', 'Can view dataconcept'),
        )

    def __len__(self):
        return self.fields.count()


class ConceptField(BasePlural):
    "Through model between DataConcept and DataField relationships."
    datafield = models.ForeignKey(DataField, related_name='concept_fields')
    concept = models.ForeignKey(DataConcept, related_name='concept_fields')
    order = models.FloatField(null=True, db_column='_order')

    class Meta(object):
        ordering = ('order',)

    def __unicode__(self):
        return unicode(self.name or self.datafield.name)

    def get_plural_name(self):
        return self.name_plural or self.datafield.get_plural_name()


# Register instance-level cache invalidation handlers
post_save.connect(post_save_cache, sender=DataField)
post_save.connect(post_save_cache, sender=DataConcept)
post_save.connect(post_save_cache, sender=Category)

pre_delete.connect(pre_delete_uncache, sender=DataField)
pre_delete.connect(pre_delete_uncache, sender=DataConcept)
pre_delete.connect(pre_delete_uncache, sender=Category)

# If django-reversion is installed, register the models
if 'reversion' in settings.INSTALLED_APPS:
    import reversion
    reversion.register(DataField)
    reversion.reversion(ConceptField)
    reversion.register(DataConcept, follow=['concept_fields'])
    reversion.register(Category)

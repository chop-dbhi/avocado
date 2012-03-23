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
from django.utils.importlib import import_module
from avocado.conf import settings as _settings
from avocado.managers import FieldManager, ConceptManager
from avocado.core import binning
from avocado.formatters import registry as formatters
from avocado.query.translators import registry as translators
from modeltree.tree import MODELTREE_DEFAULT_ALIAS, trees

__all__ = ('Category', 'Concept', 'Field')

def get_form_class(name):
    # infers this is a path
    if '.' in name:
        path = name.split('.')[:-1]
        mod = import_module(path)
    # use the django forms module
    else:
        if not name.endswith('Field'):
            name = name + 'Field'
        mod = forms
    return getattr(mod, name)

class Base(models.Model):
    """Base abstract class containing general metadata.

        ``name`` - The name _should_ be unique in practice, but is not enforced
        since in certain cases the name differs relative to the model and/or
        concepts these fields are asssociated with.

        ``name_plural`` - Same as ``name``, but the plural form. If not provided,
        an 's' will appended to the end of the ``name``.

        ``description`` - Will tend to be exposed in client applications since
        it provides context to the end-users.

        ``keywords`` - Additional extraneous text that cannot be derived from the
        name, description or data itself. This is solely used for search indexing.
    """
    name = models.CharField(max_length=50)
    name_plural = models.CharField('name (plural form)', max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True

    def __unicode__(self):
        return unicode(self.name)

    @property
    def descriptors(self):
        return {
            'name': self.name,
            'name_plural': self.name_plural,
            'description': self.description,
            'keywords': self.keywords,
        }

    def get_plural_name(self):
        return self.name_plural or (self.name + 's')


class Field(Base):
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

    # Enables this field to be accessible for use. When ``published``
    # is false, it is globally not accessible.
    published = models.BooleanField(default=False)

    objects = FieldManager()

    class Meta(object):
        app_label = 'avocado'
        unique_together = ('app_name', 'model_name', 'field_name')
        ordering = ('name',)
        permissions = (
            ('view_field', 'Can view field'),
        )

    def __unicode__(self):
        if self.name:
            return u'%s [%s]' % (self.name, self.model_name)
        return u'.'.join([self.app_name, self.model_name, self.field_name])

    # The natural key should be used any time fields are being exported
    # for integration in another system. It makes it trivial to map to new
    # data models since there are discrete parts (as suppose to using the
    # primary key).
    def natural_key(self):
        return (self.app_name, self.model_name, self.field_name)

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

    def _get_internal_type(self):
        datatype = self.field.get_internal_type().lower()
        # trim 'field' off the end
        if datatype.endswith('field'):
            datatype = datatype[:-5]
        return datatype

    @property
    def datatype(self):
        """Returns the datatype of the field this field represents.

        By default, it will use the field's internal type, but can be overridden
        by the ``INTERNAL_DATATYPE_MAP`` setting.
        """
        datatype = self._get_internal_type()
        # if a mapping exists, replace the datatype
        if datatype in _settings.INTERNAL_DATATYPE_MAP:
            datatype = _settings.INTERNAL_DATATYPE_MAP[datatype]
        return datatype

    @property
    def values(self):
        "Introspects the data and returns a distinct list of the values."
        if self.enable_choices:
            return self.model.objects.values_list(self.field_name,
                flat=True).order_by(self.field_name).distinct()

    @property
    def mapped_values(self):
        if self.enable_choices:
            # Iterate over each value and attempt to get the mapped choice
            # other fallback to the value itself
            return [smart_unicode(_settings.DATA_CHOICES_MAP.get(value, value)) \
                for value in self.values]

    @property
    def coded_values(self):
        "Returns a distinct set of coded values for this field"
        if self.enable_choices:
            values = list(self.values)
            return zip(values, xrange(len(values)))

    @property
    def choices(self):
        "Returns a distinct set of choices for this field."
        if self.enable_choices:
            return zip(self.values, self.mapped_values)

    @property
    def distribution(self, *args, **kwargs):
        "Returns a binned distribution of this field's data."
        name = self.field_name
        queryset = self.model.objects.values(name)
        return binning.distribution(queryset, name, self.datatype, *args, **kwargs)

    def query_string(self, operator=None, using=MODELTREE_DEFAULT_ALIAS):
        return trees[using].query_string_for_field(self.field, operator)

    def translate(self, operator=None, value=None, using=MODELTREE_DEFAULT_ALIAS, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans(self, operator, value, using, **context)

    def formfield(self, **kwargs):
        """Returns the default formfield class for the represented field
        instance in addition to a few helper arguments for the constructor.
        """
        # if a form class is not specified, check to see if there is a custom
        # form_class specified for this datatype
        if not kwargs.get('form_class', None):
            datatype = self._get_internal_type()

            if datatype in _settings.INTERNAL_DATATYPE_FORMFIELDS:
                name = _settings.INTERNAL_DATATYPE_FORMFIELDS[datatype]
                kwargs['form_class'] = get_form_class(name)

        # define default arguments for the formfield class constructor
        kwargs.setdefault('label', self.name.title())

        if self.enable_choices and 'widget' not in kwargs:
            kwargs['widget'] = forms.SelectMultiple(choices=self.choices)

        # get the default formfield for the model field
        return self.field.formfield(**kwargs)


class Category(Base):
    "A high-level organization for concepts."
    # A reference to a parent Category for hierarchical categories.
    parent = models.ForeignKey('self', null=True, related_name='children')

    # Certain whole categories may not be relevant or appropriate for all
    # sites being deployed. If a category is not accessible by a certain site,
    # all subsequent data elements are also not accessible by the site.
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        sites = models.ManyToManyField(Site, blank=True, related_name='categories+')

    order = models.FloatField(null=True, db_column='_order')

    class Meta(object):
        ordering = ('order', 'name')


class Concept(Base):
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
    fields = models.ManyToManyField(Field, through='ConceptField')

    # Certain concepts may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        sites = models.ManyToManyField(Site, blank=True, related_name='concepts+')

    order = models.FloatField(null=True, db_column='_order')

    # Enables this field to be accessible for use. when ``published``
    # is false, it is globally not accessible.
    published = models.BooleanField(default=False)

    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields
    formatter = models.CharField(max_length=100, blank=True, null=True,
        choices=formatters.choices)

    # Denotes whether this concept will be exposed as an interface to define
    # conditions against. concepts composed of inter-related or contextually
    # simliar fields are usually most appropriate for this option
    #conditional = models.BooleanField('Are these fields conditional?', default=True)

    objects = ConceptManager()

    class Meta(object):
        app_label = 'avocado'
        ordering = ('order',)
        permissions = (
            ('view_concept', 'Can view concept'),
        )

    def __len__(self):
        return self.fields.count()


class ConceptField(Base):
    "Through model between Concept and Field relationships."
    field = models.ForeignKey(Field, related_name='concept_fields')
    concept = models.ForeignKey(Concept, related_name='concept_fields')

    order = models.FloatField(null=True, db_column='_order')

    class Meta(object):
        ordering = ('concept', 'order')

    def __unicode__(self):
        return unicode(self.name or self.field.name)

    def get_plural_name(self):
        return self.name_plural or self.field.get_plural_name()


# If django-reversion is installed, register the models
if 'reversion' in settings.INSTALLED_APPS:
    import reversion
    reversion.register(Field)
    reversion.register(Category)
    reversion.reversion(ConceptField)
    reversion.register(Concept, follow=['concept_fields'])

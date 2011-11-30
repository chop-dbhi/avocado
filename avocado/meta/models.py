from functools import partial
from collections import OrderedDict
from datetime import datetime
from django import forms
from django.db import models, transaction
from django.contrib.sites.models import Site
from django.utils.encoding import smart_unicode
from django.db.models.fields import FieldDoesNotExist
from django.utils.importlib import import_module
from modeltree.tree import trees

from avocado.conf import settings
from avocado.meta import managers, translators, formatters

__all__ = ('Domain', 'Concept', 'Field')

DATA_CHOICES_MAP = settings.DATA_CHOICES_MAP
INTERNAL_DATATYPE_MAP = settings.INTERNAL_DATATYPE_MAP
DATATYPE_OPERATOR_MAP = settings.DATATYPE_OPERATOR_MAP
INTERNAL_DATATYPE_FORMFIELDS = settings.INTERNAL_DATATYPE_FORMFIELDS

TRANSLATOR_CHOICES = translators.registry.choices
FORMATTER_CHOICES = formatters.registry.choices

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

        ``name`` - the name _should_ be unique in practice, but is not enforced
        since in certain cases the name differs relative to the model and/or
        concepts these definitions are asssociated with

        ``description`` - will tend to be exposed in client applications since
        it provides context to the end-users

        ``keywords`` - is intended for better search indexing and most-likely will
        not be exposed in client applications
    """
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    class Meta(object):
        abstract = True
        app_label = 'avocado'

    @property
    def descriptors(self):
        return {
            'name': self.name,
            'description': self.description,
            'keywords': self.keywords,
        }

    def save(self):
        now = datetime.now()
        if not self.created:
            self.created = now
        self.modified = now
        super(Base, self).save()


class Field(Base):
    """Describes the significance and/or meaning behind some data. In addition,
    it defines the natural key of the Django field that represents the location
    of that data e.g. ``library.book.title``.
    """
    # these may vary between implementations, but the underlying field they
    # reference must be the same across implementations to ensure consistent
    # behavior of this definition
    app_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    field_name = models.CharField(max_length=50)

    # certain definitions may not be relevant or appropriate for all
    # sites being deployed. this is primarily for preventing exposure of
    # private data from certain sites. for example, there may and internal
    # and external deployment of the same site. the internal site has full
    # access to all definitions, while the external may have a limited set.
    sites = models.ManyToManyField(Site, blank=True)

    # an optional translator which customizes input query conditions
    # to a format which is suitable for the database
    translator = models.CharField(max_length=100, blank=True, null=True,
        choices=TRANSLATOR_CHOICES)

    # explicitly enable this definition to be choice-based. this should
    # only be enabled for data that contains a discrete vocabulary, i.e.
    # no full text data, most numerical data or datetime data
    enable_choices = models.BooleanField(default=False)

    # enables this definition to be accessible for use. when ``published``
    # is false, it is globally not accessible.
    published = models.BooleanField(default=False)

    objects = managers.FieldManager()

    class Meta(object):
        app_label = 'avocado'
        unique_together = ('app_name', 'model_name', 'field_name')
        ordering = ('name',)
        permissions = (
            ('view_definition', 'Can view definition'),
        )

    def __unicode__(self):
        if self.name:
            return u'%s [%s]' % (self.name, self.model_name)
        return u'.'.join([self.app_name, self.model_name, self.field_name])

    # the natural key should be used any time definitions are being exported
    # for integration in another system. it makes it trivial to map to new
    # data models since there are discrete parts (as suppose to using the
    # primary key)
    def natural_key(self):
        return (self.app_name, self.model_name, self.field_name)

    @transaction.commit_on_success
    def create_concept(self, save=False, **kwargs):
        """Derives a Concept from this Field's descriptors. Additional
        keyword arguments can be passed in to customize the new Concept object.
        The Concept can also be optionally saved by setting the ``save`` flag.
        """
        for k, v, in self.descriptors.iteritems():
            kwargs.setdefault(k, v)

        concept = Concept(**kwargs)

        if save:
            concept.save()
            condef = ConceptDefintion(definition=self, concept=concept)
            concept.conceptdefinitions.add(condef)

        return concept

    @property
    def model(self):
        "Returns the model class this definition is associated with."
        if not hasattr(self, '_model'):
            self._model = models.get_model(self.app_name, self.model_name)
        return self._model

    @property
    def field(self):
        "Returns the field object this definition represents."
        if not hasattr(self, '_field'):
            try:
                self._field = self.model._meta.get_field_by_name(self.field_name)[0]
            except FieldDoesNotExist:
                self._field = None
        return self._field

    def _get_internal_type(self):
        datatype = self.field.get_internal_type().lower()
        # trim 'field' off the end
        if datatype.endswith('field'):
            datatype = datatype[:-5]
        return datatype

    @property
    def datatype(self):
        """Returns the datatype of the field this definition represents.

        By default, it will use the field's internal type, but can be overridden
        by the ``INTERNAL_DATATYPE_MAP`` setting.
        """
        if not hasattr(self, '_datatype'):
            datatype = self._get_internal_type()
            # if a mapping exists, replace the datatype
            if INTERNAL_DATATYPE_MAP.has_key(datatype):
                datatype = INTERNAL_DATATYPE_MAP[datatype]

            self._datatype = datatype
        return self._datatype

    @property
    def operators(self):
        operators = DATATYPE_OPERATOR_MAP[self.datatype]
        # the ``isnull`` operator is a special case since all datatypes can
        # be nullable. this merely checks to see if the field allows null
        # values.
        if self.field.null:
            operators = operators + ('isnull', '-isnull')
        return operators

    @property
    def has_choices(self):
        return self.enable_choices or self.datatype == 'boolean'

    @property
    def values(self):
        "Introspects the data and returns a distinct list of the values."
        return self.model.objects.values_list(self.field_name,
            flat=True).order_by(self.field_name).distinct()

    @property
    def choices(self):
        "Returns a distinct set of choices for this field."
        if self.has_choices:
            values = self.values
            # iterate over each value and attempt to get the mapped choice
            # other fallback to the value itself
            svalues = (smart_unicode(DATA_CHOICES_MAP.get(v, v)) for v in values)
            return zip(values, svalues)

    def translate(self, operator=None, value=None, using=None, **context):
        trans = translators.registry[self.translator]()
        return trans(self, operator, value, using, **context)

    def query_string(self, operator=None, using=None):
        tree = trees[using]
        return tree.query_string_for_field(self.field, operator=operator)

    def distribution(self, exclude=[], min_count=None, max_points=20,
        order_by='field', smooth=0.01, annotate_by='id', **filters):
        pass

    def formfield(self, **kwargs):
        """Returns the default formfield class for the represented field
        instance in addition to a few helper arguments for the constructor.
        """
        # if a form class is not specified, check to see if there is a custom
        # form_class specified for this datatype
        if not kwargs.get('form_class', None):
            datatype = self._get_internal_type()

            if datatype in INTERNAL_DATATYPE_FORMFIELDS:
                name = INTERNAL_DATATYPE_FORMFIELDS[datatype]
                kwargs['form_class'] = get_form_class(name)

        # define default arguments for the formfield class constructor
        kwargs.setdefault('label', self.name.title())

        if self.has_choices and 'widget' not in kwargs:
            kwargs['widget'] = forms.SelectMultiple(choices=self.choices)

        # get the default formfield for the model field
        return self.field.formfield(**kwargs)


class Domain(Base):
    "A high-level organization for concepts."
    # a reference to a parent Domain if necessary. for simplicity's sake,
    # a domain can only be one level deep, meaning any domain that is
    # referenced as a parent, cannot have a parent itself.
    parent = models.ForeignKey('self', null=True, related_name='children',
        limit_choices_to={'parent__isnull': True})

    # certain whole domains may not be relevant or appropriate for all
    # sites being deployed. if a domain is not accessible by a certain site,
    # all subsequent data elements are also not accessible by the site
    # TODO find a use case for the ``sites`` m2m below
    # sites = models.ManyToManyField(Site, blank=True)

    class Meta(object):
        app_label = 'avocado'
        order_with_respect_to = 'parent'
        ordering = ('name',)

    def __unicode__(self):
        return u'{}'.format(self.name)


class Concept(Base):
    """Our acceptance of an ontology is, I think, similar in principle to our
    acceptance of a scientific theory, say a system of physics; we adopt, at
    least insofar as we are reasonable, the simplest conceptual scheme into
    which the disordered fragments of raw experience can be fitted and arranged.

        -- Willard Van Orman Quine
    """


    # although a domain does not technically need to be defined, this more
    # for workflow reasons than for when the concept is published. automated
    # prcesses may create concepts on the fly, but not know which domain they
    # should be linked to initially. the admin interface enforces choosing a
    # domain when the concept is published
    domain = models.ForeignKey(Domain, null=True)

    # the associated definitions for this concept. definitions can be
    # associated with multiple concepts, thus the M2M
    definitions = models.ManyToManyField(Field,
        through='ConceptDefintion')

    order = models.FloatField(default=0,
        help_text=u'Ordering should be relative to the domain')

    # enables this definition to be accessible for use. when ``published``
    # is false, it is globally not accessible.
    published = models.BooleanField(default=False)

    # an optional formatter which provides custom formatting for this
    # concept relative to the associated definitions
    formatter = models.CharField(max_length=100, blank=True, null=True,
        choices=FORMATTER_CHOICES)

    # below are various booleans for denoting the usages of this concept with
    # respect to a SQL query. these flags are not mutually exclusive and in
    # most cases than not will have most or all of these flags enabled for
    # robust interfaces for these concepts.

    # denotes whether this concept should exposed for data exporting. this
    # should be decided based on the underlying data representing this
    # concept.
    select_enabled = models.BooleanField(default=True)

    # denotes whether this concept will be exposed as an interface to define
    # conditions against. concepts composed of inter-related or contextually
    # simliar definitions are usually most appropriate for this option
    where_enabled = models.BooleanField(default=True)

    class Meta(object):
        app_label = 'avocado'
        order_with_respect_to = 'domain'
        ordering = ('order',)
        permissions = (
            ('view_concept', 'Can view concept'),
        )

    def __unicode__(self):
        return u'{}'.format(self.name)

    def __len__(self):
        return self.definitions.count()

    def get_formatter(self, preferred_formats=None):
        """Returns a partially evaluated formatter function given a list of
        ``preferred_formats``.
        """
        formatter = formatters.registry[self.formatter]

        if preferred_formats:
            for x in preferred_formats:
                if x in formatter:
                    formatter = partial(formatter, choice=x)
                    break
        else:
            formatter = partial(formatter)

        formatter.length = len(self)
        return formatter

    def _get_formatter_value(self, cdefinition, value, name=None):
        definition = cdefinition.definition

        key = '{}' % definition.field_name

        if name is None:
            name = cdefinition.name or definition.name

        data = {
            'name': name,
            'value': value,
            'definition': definition,
        }

        return key, data

    def get_formatter_values(self, values):
        """Returns an ``OrderedDict`` representing a mapping between the
        associated definitions and the given values.
        """
        new_values = OrderedDict()
        cdefs = self.conceptdefinitions.select_related('definition')

        if len(cdefs) == 1:
            tup = self._get_formatter_value(cdefs[0], value=values[0],
                name=cdefs[0].name)
            new_values.update(tup)
        else:
            for i, cdef in enumerate(cdefs):
                tup = self._get_formatter_value(cdef, value=values[i])
                new_values.update(tup)

        return new_values


class ConceptDefintion(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    order = models.FloatField(null=True)

    definition = models.ForeignKey(Field)
    concept = models.ForeignKey(Concept)

    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    class Meta(object):
        app_label = 'avocado'

    def save(self):
        now = datetime.now()
        if not self.created:
            self.created = now
        self.modified = now
        super(ConceptDefintion, self).save()


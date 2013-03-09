import re
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_delete
from django.core.validators import RegexValidator
from avocado import managers
from avocado.core.models import Base, BasePlural
from avocado.core.cache.model import post_save_cache, pre_delete_uncache
from avocado.query.models import AbstractDataView, AbstractDataContext, AbstractDataQuery
from avocado.query.translators import registry as translators
from avocado.query.operators import registry as operators
from avocado.events.models import Log
from avocado import formatters
from avocado import interfaces


__all__ = ('DataCategory', 'DataConcept', 'DataField',
    'DataContext', 'DataView', 'DataQuery')


ident_re = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
validate_ident = RegexValidator(ident_re, _("Enter a valid 'identifier' " \
    "that is a valid Python variable name."), 'invalid')


class DataCategory(Base):
    "A high-level organization for data concepts."
    # A reference to a parent for hierarchical categories
    parent = models.ForeignKey('self', null=True, blank=True,
        related_name='children', limit_choices_to={'parent__isnull': True},
        help_text='Sub-categories are limited to one-level deep')
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = managers.DataCategoryManager()

    class Meta(object):
        ordering = ('-parent__id', 'order', 'name')
        verbose_name_plural = 'data categories'


class DataField(BasePlural):
    """Describes the significance and/or meaning behind some data. In addition,
    it defines the natural key of the Django field that represents the location
    of that data e.g. ``library.book.title``.
    """
    app_name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=200)
    field_name = models.CharField(max_length=200)

    internal = models.BooleanField(default=False,
        help_text='Flag for internal use and does not abide by the published' \
            'and archived rules.')

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

    # Set this field to true to make this field's values enumerable. This
    # should only be enabled for data that contains a discrete vocabulary, i.e.
    # no full text data.
    enumerable = models.BooleanField(default=False)

    # An optional translator which customizes input query conditions
    # to a format which is suitable for the database.
    translator = models.CharField(max_length=100, blank=True, null=True,
        choices=translators.choices)

    # Associate a specific interface class to this field
    interface = models.CharField(max_length=100, blank=True, null=True,
        choices=interfaces.registry.choices)

    # The timestamp of the last time the underlying data for this field
    # has been modified. This is used for the cache key and for general
    # reference. The underlying table may not have a timestamp nor is it
    # optimal to have to query the data for the max `modified` time.
    data_modified = models.DateTimeField(null=True, help_text='The last time '\
        ' the underlying data for this field was modified.')

    group = models.ForeignKey(Group, null=True, blank=True, related_name='fields+')

    # Certain fields may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    sites = models.ManyToManyField(Site, blank=True, related_name='fields+')

    # The order of this datafield with respect to the category (if defined).
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = managers.DataFieldManager()

    class Meta(object):
        unique_together = ('app_name', 'model_name', 'field_name')
        ordering = ('name',)
        permissions = (
            ('view_datafield', 'Can view datafield'),
        )

    @classmethod
    def init(cls, app_name, model_name=None, field_name=None, **kwargs):
        """Convenience method for initializing a new instance with metadata
        populated directly from the model field instance. This returns an
        _unsaved_ instance.
        """
        # Field instance
        if isinstance(app_name, models.Field):
            field = app_name
            field_name = field.name
            model_name = field.model.module_name
            app_name = field.model._meta.app_label

        # Dot-delimited string
        elif isinstance(app_name, basestring) and '.' in app_name:
            values = app_name.split('.')
            if len(values) != 3:
                raise ValueError("The dot-delimited field format must be 'app.model.field'.")
            app_name, model_name, field_name = values

        defaults = {
            'app_name': app_name,
            'model_name': model_name.lower(),
            'field_name': field_name,
        }

        # Temp instance to validate the model field exists
        f = cls(**defaults)
        if not f.field:
            raise ValueError('Field does not correspond to a model field.')

        # Add field-derived components
        defaults.update({
            'name': f.field.verbose_name.title(),
            'description': f.field.help_text or None,
        })

        # Update defaults with kwargs
        defaults.update(kwargs)

        return cls(**defaults)

    def __init__(self, *args, **kwargs):
        super(DataField, self).__init__(*args, **kwargs)

        # To prevent having an object.__getattribute__ circus below..
        self._model = None
        self.__interface = None

    def __unicode__(self):
        if self.field:
            return unicode(self._interface)
        if self.name:
            return self.name
        return u'{0}.{1}.{2}'.format(self.app_name, self.model_name, self.field_name)

    def __len__(self):
        return self.size()

    def __nonzero__(self):
        "Takes precedence over __len__, so it is always truthy."
        return True

    def __getattr__(self, attr):
        "Implement to fallback to using the _interface for this instance."
        # No private or magic methods allowed
        if not attr.startswith('_') and self._interface:
            try:
                return getattr(self._interface, attr)
            except AttributeError:
                pass
        raise AttributeError("'{0}' object has no attribute '{1}'".format(type(self).__name__, attr))

    @property
    def _interface(self):
        if self.__interface is None and self.field:
            if self.interface:
                klass = interfaces.registry.get(self.interface)
            else:
                klass = interfaces.get_interface(self.field)
            self.__interface = klass(self)
        return self.__interface

    @property
    def model(self):
        "Returns the model class this datafield is associated with."
        if self._model is None:
            self._model = models.get_model(self.app_name, self.model_name)
        return self._model

    @property
    def field(self):
        "Returns the field object this datafield is associated with."
        if self.model:
            try:
                return self.model._meta.get_field_by_name(self.field_name)[0]
            except models.FieldDoesNotExist:
                pass

    def save(self, *args, **kwargs):
        # Ensure a name has been set
        if not self.name:
            self.name = unicode(self)
        return super(DataField, self).save(*args, **kwargs)

    # The natural key should be used any time fields are being exported
    # for integration in another system. It makes it trivial to map to new
    # data models since there are discrete parts (as suppose to using the
    # primary key).
    def natural_key(self):
        return self.app_name, self.model_name, self.field_name

    def get_plural_unit(self):
        if self.unit_plural:
            plural = self.unit_plural
        elif self.unit and not self.unit.endswith('s'):
            plural = self.unit + 's'
        else:
            plural = self.unit
        return plural


    # Translator Convenience Methods

    @property
    def operators(self):
        "Returns the valid operators for this datafield."
        trans = translators[self.translator]
        return [(x, operators[x].verbose_name) for x in trans.get_operators(self)]

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
    which the disordered fragments of raw experience can be fitted and
    arranged.

        -- Willard Van Orman Quine
    """

    ident = models.CharField(max_length=100, null=True,
        blank=True, validators=[validate_ident],
        help_text='Unique identifier that can be used for programmatic access')

    internal = models.BooleanField(default=False,
        help_text='Flag for internal use and does not abide by the published' \
            'and archived rules.')

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

    group = models.ForeignKey(Group, null=True, blank=True,
        related_name='concepts+')

    # Certain concepts may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    sites = models.ManyToManyField(Site, blank=True, related_name='concepts+')

    order = models.FloatField(null=True, blank=True, db_column='_order')

    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields. If a formatter is not
    # defined, this DataConcept is not intended to be exposed since the
    # underlying data may not be appropriate for client consumption.
    formatter_name = models.CharField('formatter', max_length=100, blank=True,
        null=True, choices=formatters.registry.choices)

    # A flag that denotes this concept is 'queryable' which assumes fields
    # that DO NOT result in a nonsensicle representation of the concept.
    queryable = models.BooleanField(default=True)

    # A flag that denotes when this concept can be applied to an ORDER BY
    # Certain concepts are not appropriate because they are too complicated,
    # or a very specific abstraction that does not order by what it actually
    # represents.
    sortable = models.BooleanField(default=True)

    objects = managers.DataConceptManager()

    def format(self, *args, **kwargs):
        """Convenience method for formatting data relative to this concept's
        associated formatter. To prevent redundant initializations (say, in
        a tight loop) the formatter instance is cached until the formatter
        name changes.
        """
        name = self.formatter_name
        cache = getattr(self, '_formatter_cache', None)
        if not cache or name != cache[0]:
            formatter = formatters.registry.get(name)(self)
            self._formatter_cache = (name, formatter)
        else:
            formatter = cache[1]
        return formatter(*args, **kwargs)

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


class DataContext(AbstractDataContext, Base):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True, related_name='datacontext+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    objects = managers.DataContextManager()

    def __unicode__(self):
        toks = []

        # Identifier
        if self.name:
            toks.append(self.name)
        elif self.user_id:
            toks.append(unicode(self.user))
        elif self.session_key:
            toks.append(self.session_key)
        elif self.pk:
            toks.append('#{0}'.format(self.pk))
        else:
            toks.append('unsaved')

        # State
        if self.default:
            toks.append('default template')
        elif self.template:
            toks.append('template')
        elif self.session:
            toks.append('session')
        elif self.archived:
            toks.append('archived')
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def archive(self):
        if self.archived:
            return False
        backup = self.pk, self.session, self.archived
        self.pk, self.session, self.archived = None, False, True
        self.save()
        self.pk, self.session, self.archived = backup
        return True

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True, default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


class DataView(AbstractDataView, Base):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `SELECT` and `ORDER BY` statements in a SQL query.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True, related_name='dataview+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    objects = managers.DataViewManager()

    def __unicode__(self):
        toks = []

        # Identifier
        if self.name:
            toks.append(self.name)
        elif self.user_id:
            toks.append(unicode(self.user))
        elif self.session_key:
            toks.append(self.session_key)
        elif self.pk:
            toks.append('#{0}'.format(self.pk))
        else:
            toks.append('unsaved')

        # State
        if self.default:
            toks.append('default template')
        elif self.template:
            toks.append('template')
        elif self.session:
            toks.append('session')
        elif self.archived:
            toks.append('archived')
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def archive(self):
        if self.archived:
            return False
        backup = self.pk, self.session, self.archived
        self.pk, self.session, self.archived = None, False, True
        self.save()
        self.pk, self.session, self.archived = backup
        return True

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True, default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


class DataQuery(AbstractDataQuery, Base):
    """
    JSON object representing a complete query.

    The query is constructed from a context(providing the 'WHERE' statements)
    and a view(providing the 'SELECT' and 'ORDER BY" statements). This
    corresponds to all the statements of the SQL query to dictate what info
    to retrieve, how to filter it, and the order to display it in.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True, related_name='dataquery+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    objects = managers.DataQueryManager()

    def __unicode__(self):
        toks = []

        # Identifier
        if self.name:
            toks.append(self.name)
        elif self.user_id:
            toks.append(unicode(self.user))
        elif self.session_key:
            toks.append(self.session_key)
        elif self.pk:
            toks.append('#{0}'.format(self.pk))
        else:
            toks.append('unsaved')

        # State
        if self.default:
            toks.append('default template')
        elif self.template:
            toks.append('template')
        elif self.session:
            toks.append('session')
        elif self.archived:
            toks.append('archived')
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def archive(self):
        if self.archived:
            return False
        backup = self.pk, self.session, self.archived
        self.pk, self.session, self.archived = None, False, True
        self.save()
        self.pk, self.session, self.archived = backup
        return True

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True, default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


# Register instance-level cache invalidation handlers
post_save.connect(post_save_cache, sender=DataField)
post_save.connect(post_save_cache, sender=DataConcept)
post_save.connect(post_save_cache, sender=DataCategory)

pre_delete.connect(pre_delete_uncache, sender=DataField)
pre_delete.connect(pre_delete_uncache, sender=DataConcept)
pre_delete.connect(pre_delete_uncache, sender=DataCategory)

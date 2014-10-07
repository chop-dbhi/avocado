import re
import logging
import random
from warnings import warn
from datetime import datetime
from django.db import models
from django.db.models import Count
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django.db.models.signals import post_save, pre_delete
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from avocado.core import utils
from avocado.core.structures import ChoicesDict
from avocado.core.models import Base, BasePlural, PublishArchiveMixin
from avocado.core.cache import post_save_cache, pre_delete_uncache, \
    cached_method
from avocado.conf import settings, dep_supported
from avocado import managers, history
from avocado.query.models import AbstractDataView, AbstractDataContext, \
    AbstractDataQuery
from avocado.query.translators import registry as translators
from avocado.query.operators import registry as operators
from avocado.lexicon.models import Lexicon
from avocado.stats.agg import Aggregator
from avocado import formatters


__all__ = ('DataCategory', 'DataConcept', 'DataField',
           'DataContext', 'DataView', 'DataQuery')

log = logging.getLogger(__name__)


ident_re = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
validate_ident = RegexValidator(ident_re, _("Enter an 'identifier' that is a "
                                "valid Python variable name."),
                                'invalid')


def is_lexicon(f):
    """Returns true if the model is a subclass of Lexicon and this
    is the pk field. All other fields on the class are treated as
    normal datafields.
    """
    warn('Lexicon detection in the DataField API is deprecated and '
         'will be removed in 2.4. Set the alternate fields explicitly '
         'on the field instance', DeprecationWarning)
    return f.model and issubclass(f.model, Lexicon) \
        and f.field == f.model._meta.pk


def is_objectset(f):
    """Returns true if the model is a subclass of ObjectSet and this
    is the pk field. All other fields on the class are treated as
    normal datafields.
    """
    warn('ObjectSet detection in the DataField API is deprecated and '
         'will be removed in 2.4. Set the alternate fields explicitly '
         'on the field instance', DeprecationWarning)

    if dep_supported('objectset'):
        from objectset.models import ObjectSet

        return f.model and issubclass(f.model, ObjectSet) \
            and f.field == f.model._meta.pk

    return False


class DataCategory(Base, PublishArchiveMixin):
    "A high-level organization for data concepts."
    # A reference to a parent for hierarchical categories
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children',
                               limit_choices_to={'parent__isnull': True},
                               help_text='Sub-categories are limited to '
                               'one-level deep')
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = managers.DataCategoryManager()

    class Meta(object):
        ordering = ('parent__order', 'parent__name', 'order', 'name')
        verbose_name_plural = 'data categories'


class DataField(BasePlural, PublishArchiveMixin):
    """Describes the significance and/or meaning behind some data. In addition,
    it defines the natural key of the Django field that represents the location
    of that data e.g. ``library.book.title``.
    """
    # App/model/field represent the natural key of this field based on
    # Django's methods of distinguishing models.
    app_name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=200)
    field_name = models.CharField(max_length=200)

    # Supplementary fields that respresent alternate representations
    # of the base field
    label_field_name = models.CharField(max_length=200, null=True, blank=True,
                                        help_text='Label field to the '
                                                  'reference field')
    search_field_name = models.CharField(max_length=200, null=True, blank=True,
                                         help_text='Search field to the '
                                                   'reference field')

    order_field_name = models.CharField(max_length=200, null=True, blank=True,
                                        help_text='Order field to the '
                                                  'reference field')

    code_field_name = models.CharField(max_length=200, null=True, blank=True,
                                       help_text='Order field to the '
                                                 'reference field')

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

    # Set this field to False if you wish to exclude this field's data from the
    # Haystack index.
    indexable = models.BooleanField(default=True)

    type = models.CharField(max_length=100, blank=True, null=True,
                            help_text='Logical type of this field. Typically '
                                      'used downstream for defining behavior '
                                      'and semantics around the field.')

    # An optional translator which customizes input query conditions
    # to a format which is suitable for the database.
    translator = models.CharField(max_length=100, blank=True, null=True,
                                  choices=translators.choices)

    # This is used for the cache key to check if the cached values is stale.
    data_version = models.IntegerField(default=1, help_text='The current '
                                       'version of the underlying data for '
                                       'this field as of the last '
                                       'modification/update.')

    group = models.ForeignKey(Group, null=True, blank=True,
                              related_name='fields+')

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

    internal = models.BooleanField(default=False, help_text='Flag for '
                                   'internal use and does not abide by the '
                                   'published and archived rules.')

    objects = managers.DataFieldManager()

    class Meta(object):
        unique_together = ('app_name', 'model_name', 'field_name')
        ordering = ('category__order', 'category__name', 'order', 'name')
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
                raise ValueError("The dot-delimited field format must "
                                 "be 'app.model.field'.")
            app_name, model_name, field_name = values

        defaults = {
            'app_name': app_name,
            'model_name': model_name.lower(),
            'field_name': field_name,
        }

        # Temp instance to validate the model field exists
        f = cls(**defaults)

        if not f.model:
            raise ValueError('Unknown model {0}'.format(f.model_name))

        if not f.field:
            raise ValueError('Unknown field {0} on model {1}.'
                             .format(f.field_name, f.model_name))

        # Add field-derived components
        defaults.update({
            'name': f.field.verbose_name.title(),
            'description': f.field.help_text or None,
        })

        # Update defaults with kwargs
        defaults.update(kwargs)

        return cls(**defaults)

    def __unicode__(self):
        if self.name:
            return self.name
        return u'{0} {1}'.format(self.model._meta.verbose_name,
                                 self.field.verbose_name).title()

    def __len__(self):
        return self.size()

    def __nonzero__(self):
        "Takes precedence over __len__, so it is always truthy."
        return True

    # The natural key should be used any time fields are being exported
    # for integration in another system. It makes it trivial to map to new
    # data models since there are discrete parts (as suppose to using the
    # primary key).
    def natural_key(self):
        return self.app_name, self.model_name, self.field_name

    # Django Model Field-related Properties and Methods

    @property
    def real_model(self):
        "Returns the model class this datafield is associated with."
        if not hasattr(self, '_real_model'):
            self._real_model = models.get_model(self.app_name, self.model_name)
        return self._real_model

    @property
    def real_field(self):
        "Returns the field object this datafield is associated with."
        if self.real_model:
            try:
                return self.real_model._meta.get_field(self.field_name)
            except FieldDoesNotExist:
                pass

    @property
    def model(self):
        "Returns the model class this datafield represents."
        real_field = self.real_field
        # Handle foreign key fields to a Lexicon model
        if real_field and isinstance(real_field, models.ForeignKey) \
                and issubclass(real_field.rel.to, Lexicon):
            return real_field.rel.to
        return self.real_model

    @property
    def field(self):
        "Returns the field object this datafield represents."
        model = self.model

        if model:
            if issubclass(model, Lexicon):
                return model._meta.pk

            if dep_supported('objectset'):
                from objectset.models import ObjectSet

                if issubclass(model, ObjectSet):
                    return model._meta.pk

        return self.real_field

    @property
    def lexicon(self):
        return is_lexicon(self)

    @property
    def objectset(self):
        return is_objectset(self)

    @property
    def value_field_name(self):
        "Alias for field name."
        return self.field_name

    @property
    def value_field(self):
        "Alias for field."
        return self.field

    @property
    def label_field(self):
        "Returns the label field object for this datafield."
        model = self.model

        if model:
            field_name = None

            if self.label_field_name:
                field_name = self.label_field_name
            elif is_lexicon(self):
                field_name = 'label'
            elif is_objectset(self):
                if hasattr(self.model, 'label_field'):
                    field_name = self.model.label_field
                else:
                    field_name = 'pk'

            if field_name:
                try:
                    return model._meta.get_field(field_name)
                except FieldDoesNotExist:
                    pass

        return self.field

    @property
    def search_field(self):
        "Returns the search field object for this datafield."
        model = self.model

        if model and self.search_field_name:
            try:
                return model._meta.get_field(self.search_field_name)
            except FieldDoesNotExist:
                pass

        return self.label_field

    @property
    def order_field(self):
        "Returns the order field object for this datafield."
        model = self.model

        if model:
            field_name = None

            if self.order_field_name:
                field_name = self.order_field_name
            elif is_lexicon(self):
                field_name = 'order'

            if field_name:
                try:
                    return model._meta.get_field(field_name)
                except FieldDoesNotExist:
                    pass

        return self.field

    @property
    def code_field(self):
        "Returns the code field object for this datafield."
        model = self.model

        if model:
            field_name = None

            if self.code_field_name:
                field_name = self.code_field_name
            elif is_lexicon(self):
                field_name = 'code'

            if field_name:
                try:
                    return model._meta.get_field(field_name)
                except FieldDoesNotExist:
                    pass

    @property
    def nullable(self):
        "Returns whether this field can contain NULL values."
        return self.field.null

    @property
    def internal_type(self):
        "Returns the internal type of the field this datafield represents."
        return utils.get_internal_type(self.field)

    @property
    def simple_type(self):
        """Returns a simple type mapped from the internal type."

        By default, it will use the field's internal type, but can be
        overridden by the ``SIMPLE_TYPE_MAP`` setting.
        """
        return utils.get_simple_type(self.field)

    @property
    def searchable(self):
        "Returns true if a text-field and is not an enumerable field."
        # Optimized shortcut to prevent database hit for enumerable check..
        if self.search_field == self.field:
            simple_type = utils.get_simple_type(self.field)
            return simple_type == 'string' and not self.enumerable

        return utils.is_searchable(self.search_field)

    # Convenience Methods
    # Easier access to the underlying data for this data field

    def values_list(self, order=True, distinct=True, queryset=None):
        "Returns a `ValuesListQuerySet` of values for this field."
        value_field = self.value_field.name
        order_field = self.order_field.name

        if queryset is None:
            queryset = self.model.objects.all()

        queryset = queryset.values_list(value_field, flat=True)

        if order:
            queryset = queryset.order_by(order_field)

        if distinct:
            return queryset.distinct()

        return queryset

    def labels_list(self, order=True, distinct=True, queryset=None):
        "Returns a `ValuesListQuerySet` of labels for this field."
        label_field = self.label_field.name
        order_field = self.order_field.name

        if queryset is None:
            queryset = self.model.objects.all()

        queryset = queryset.values_list(label_field, flat=True)

        if order:
            queryset = queryset.order_by(order_field)

        if distinct:
            return queryset.distinct()

        return queryset

    def codes_list(self, order=True, distinct=True, queryset=None):
        "Returns a `ValuesListQuerySet` of labels for this field."
        if not self.code_field:
            return

        code_field = self.code_field.name
        order_field = self.order_field.name

        if queryset is None:
            queryset = self.model.objects.all()

        queryset = queryset.values_list(code_field, flat=True)

        if order:
            queryset = queryset.order_by(order_field)

        if distinct:
            return queryset.distinct()

        return queryset

    def search(self, query, queryset=None):
        "Rudimentary search for string-based values."
        if utils.get_simple_type(self.search_field) == 'string':
            field_name = self.search_field.name
            filters = {u'{0}__icontains'.format(field_name): query}
            return self.values_list(queryset=queryset).filter(**filters)

    def get_plural_unit(self):
        if self.unit_plural:
            plural = self.unit_plural
        elif self.unit and not self.unit.endswith('s'):
            plural = self.unit + 's'
        else:
            plural = self.unit
        return plural

    def get_label(self, value, queryset=None):
        "Get the corresponding label to a value."
        labels = self.value_labels(queryset=queryset)

        if value in labels:
            return labels[value]

        return smart_unicode(value)

    def _has_predefined_choices(self):
        """Returns true if the base field has pre-defined choices and no
        alternative label field has been defined.
        """
        return bool(self.field.choices)

    # Data-related Cached Properties
    # These may be cached until the underlying data changes
    @cached_method(version='data_version')
    def size(self, queryset=None):
        "Returns the count of distinct values."
        if self._has_predefined_choices():
            return len(self.field.choices)

        return self.values_list(queryset=queryset).count()

    @cached_method(version='data_version')
    def values(self, queryset=None):
        "Returns a distinct list of values."
        if self._has_predefined_choices():
            return tuple(zip(*self.field.choices)[0])

        return tuple(self.values_list(queryset=queryset))

    @cached_method(version='data_version')
    def labels(self, queryset=None):
        "Returns a distinct list of labels."
        if self._has_predefined_choices():
            labels = zip(*self.field.choices)[1]
            return tuple(smart_unicode(l) for l in labels)

        return tuple(
            smart_unicode(l) for l in self.labels_list(queryset=queryset))

    @cached_method(version='data_version')
    def codes(self, queryset=None):
        "Returns a distinct set of coded values for this field"
        if self._has_predefined_choices():
            return tuple(range(self.size(queryset=queryset)))

        if self.code_field:
            return tuple(self.codes_list(queryset=queryset))

    def value_labels(self, queryset=None):
        "Returns a distinct set of value/label pairs for this field."
        return ChoicesDict(zip(
            self.values(queryset=queryset), self.labels(queryset=queryset)))

    def coded_labels(self, queryset=None):
        "Returns a distinct set of code/label pairs for this field."
        codes = self.codes(queryset=queryset)

        if codes is not None:
            return ChoicesDict(zip(codes, self.labels(queryset=queryset)))

    def coded_values(self, queryset=None):
        "Returns a distinct set of code/value pairs for this field."
        codes = self.codes(queryset=queryset)

        if codes is not None:
            return ChoicesDict(zip(codes, self.values(queryset=queryset)))

    # Alias since it's common parlance in Django
    choices = value_labels
    coded_choices = coded_labels

    # Data Aggregation Properties
    def groupby(self, *args, **kwargs):
        return Aggregator(
            self.field, queryset=kwargs.get('queryset')).groupby(*args)

    @cached_method(version='data_version')
    def count(self, *args, **kwargs):
        "Returns an the aggregated counts."
        return Aggregator(
            self.field,
            queryset=kwargs.pop('queryset', None)).count(*args, **kwargs)

    @cached_method(version='data_version')
    def max(self, *args, **kwargs):
        "Returns the maximum value."
        return Aggregator(
            self.field, queryset=kwargs.get('queryset')).max(*args)

    @cached_method(version='data_version')
    def min(self, *args, **kwargs):
        "Returns the minimum value."
        return Aggregator(
            self.field, queryset=kwargs.get('queryset')).min(*args)

    @cached_method(version='data_version')
    def avg(self, *args, **kwargs):
        "Returns the average value. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(
                self.field, queryset=kwargs.get('queryset')).avg(*args)

    @cached_method(version='data_version')
    def sum(self, *args, **kwargs):
        "Returns the sum of values. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(
                self.field, queryset=kwargs.get('queryset')).sum(*args)

    @cached_method(version='data_version')
    def stddev(self, *args, **kwargs):
        "Returns the standard deviation. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(
                self.field,
                queryset=kwargs.get('queryset')).stddev(*args)

    @cached_method(version='data_version')
    def variance(self, *args, **kwargs):
        "Returns the variance. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(
                self.field,
                queryset=kwargs.get('queryset')).variance(*args)

    @cached_method(version='data_version')
    def sparsity(self, *args, **kwargs):
        "Returns the ratio of null values in the population."
        if 'queryset' in kwargs:
            queryset = kwargs.get('queryset')
        else:
            queryset = self.model.objects.all()

        count = queryset.count()

        # No data, 100% sparsity
        if count == 0:
            return 1.0

        isnull = '{0}__isnull'.format(self.value_field.name)
        nulls = queryset.filter(**{isnull: True}).count()

        return nulls / float(count)

    @cached_method(version='data_version')
    def dist(self, queryset=None):
        if queryset is None:
            queryset = self.model.objects.all()

        queryset = queryset.values(self.value_field.name)\
            .annotate(cnt=Count(self.value_field.name))\
            .values_list(self.value_field.name, 'cnt')\
            .order_by(self.value_field.name)

        return tuple(queryset)

    # Translator Convenience Methods
    @property
    def operators(self):
        "Returns the valid operators for this datafield."
        trans = translators[self.translator]
        return [(x, operators[x].verbose_name) for x
                in trans.get_operators(self)]

    def translate(self, operator=None, value=None, tree=None, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.translate(self, operator, value, tree, **context)

    def validate(self, operator=None, value=None, tree=None, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.validate(self, operator, value, tree, **context)

    def random(self, k, queryset=None):
        """
        Returns a k length list of values of this datafield's value population.
        """
        return random.sample(self.values(queryset=queryset), k)


class DataConcept(BasePlural, PublishArchiveMixin):
    """Our acceptance of an ontology is, I think, similar in principle to our
    acceptance of a scientific theory, say a system of physics; we adopt, at
    least insofar as we are reasonable, the simplest conceptual scheme into
    which the disordered fragments of raw experience can be fitted and
    arranged.

        -- Willard Van Orman Quine
    """

    ident = models.CharField(max_length=100, null=True, blank=True,
                             validators=[validate_ident], help_text='Unique '
                             'identifier that can be used for programmatic '
                             'access')

    internal = models.BooleanField(default=False, help_text='Flag for '
                                   'internal use and does not abide by '
                                   'the published and archived rules.')

    type = models.CharField(max_length=100, blank=True, null=True)

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
    # concept relative to the associated fields.
    formatter_name = models.CharField('formatter', max_length=100, blank=True,
                                      null=True,
                                      choices=formatters.registry.choices)

    # A flag that denotes this concept is viewable, that is, this the concept
    # is appropriate to be used as a viewable interface. Non-viewable concepts
    # can be used to prevent exposing underlying data that may not be
    # appropriate for client consumption.
    viewable = models.BooleanField(default=True)

    # A flag that denotes this concept is 'queryable' which assumes fields
    # that DO NOT result in a nonsensicle representation of the concept.
    queryable = models.BooleanField(default=True)

    # A flag that denotes when this concept can be applied to an ORDER BY
    # Certain concepts are not appropriate because they are too complicated,
    # or a very specific abstraction that does not order by what it actually
    # represents.
    sortable = models.BooleanField(default=True)

    # Set this field to False if you wish to exclude DataFields associated
    # with this concept from the Haystack index.
    indexable = models.BooleanField(default=True)

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
        ordering = ('category__order', 'category__name', 'order', 'name')
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
        ordering = ('order', 'name')

    def __unicode__(self):
        return self.name or unicode(self.field)

    def get_plural_name(self):
        if self.name_plural:
            return self.name_plural

        if self.name:
            if not self.name.endswith('s'):
                return self.name + 's'
            return self.name

        return self.field.get_plural_name()


class DataContext(AbstractDataContext, Base):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # The parent this instance was derived from
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='forks')

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='datacontext+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    accessed = models.DateTimeField(default=datetime.now(), editable=False)
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
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True,
                                                     default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be '
                                      'defined')

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

    # The parent this instance was derived from
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='forks')

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='dataview+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    accessed = models.DateTimeField(default=datetime.now(), editable=False)
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
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True,
                                                     default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be '
                                      'defined')

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

    # The parent this instance was derived from
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='forks')

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='dataquery+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    accessed = models.DateTimeField(default=datetime.now, editable=False)
    objects = managers.DataQueryManager()
    shared_users = models.ManyToManyField(User,
                                          related_name='shareddataquery+')

    # Flag indicating whether this is a public query or not. Public queries are
    # visible to all other users of the system while non-public queries are
    # only visible to the query owner and those in the shared_users collection.
    public = models.BooleanField(default=False)

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
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True,
                                                     default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be '
                                      'defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def share_with_user(self, username_or_email, create_user=True):
        """
        Attempts to add a user with the supplied email address or username
        to the list of shared users for this query. If create_user is set to
        True, users will be created for emails that are not already associated
        with an existing user. New users are not created for a provided
        username if it cannot be found.

        Returns True if the email/username was added to the list of shared
        users and False if the email/username wasn't added because it already
        exists or wasn't created.
        """

        # If both share setttings are set to false, nothing can be done
        if not settings.SHARE_BY_USERNAME and not settings.SHARE_BY_EMAIL:
            log.warning('Cannot share with any user because SHARE_BY_USERNAME'
                        ' and SHARE_BY_EMAIL are both set to False.')
            return False

        # If the query is already shared then there is no need to share it
        # again.
        if self.shared_users.filter(
                Q(email__iexact=username_or_email) |
                Q(username__iexact=username_or_email)).exists():
            return False

        user = None

        # Create a Q() object to build our query
        q = Q()

        if settings.SHARE_BY_USERNAME:
            if settings.SHARE_BY_USERNAME_CASE_SENSITIVE:
                q |= Q(username=username_or_email)
            else:
                q |= Q(username__iexact=username_or_email)

        if settings.SHARE_BY_EMAIL:
            q |= Q(email__iexact=username_or_email)

        # Try to retrive a user. If this fails, create a new user with the
        # email address
        try:
            user = User.objects.get(q)
        except User.DoesNotExist:
            log.warning('Cannot find user with '.format(username_or_email))

        if not user and create_user:
            try:
                user = utils.create_email_based_user(username_or_email)
            except ValidationError:
                log.warning('Could not create user with email. "{0}" is not a '
                            'valid email.'.format(username_or_email))

        # If a user was found/created, add that user to shared users
        if user:
            self.shared_users.add(user)
            self.save()
            return True

        return False

# Register instance-level cache invalidation handlers
post_save.connect(post_save_cache, sender=DataField)
post_save.connect(post_save_cache, sender=DataConcept)
post_save.connect(post_save_cache, sender=DataCategory)

pre_delete.connect(pre_delete_uncache, sender=DataField)
pre_delete.connect(pre_delete_uncache, sender=DataConcept)
pre_delete.connect(pre_delete_uncache, sender=DataCategory)

# Register with history API
if settings.HISTORY_ENABLED:
    history.register(DataContext, fields=('name', 'description', 'json'))
    history.register(DataView, fields=('name', 'description', 'json'))
    history.register(DataQuery, fields=('name', 'description', 'context_json',
                                        'view_json'))

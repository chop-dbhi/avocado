import logging
from django.db import models
from django.db.models import Q
from django.db import transaction
from django.conf import settings as djsettings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.manager import ManagerDescriptor
from avocado.conf import OPTIONAL_DEPS, dep_supported, settings
from avocado.core.managers import PublishedManager, PublishedQuerySet


logger = logging.getLogger(__name__)


# [2014-11-05] HACK to resolve this issue:
# https://github.com/toastdriven/django-haystack/issues/1009
if OPTIONAL_DEPS['haystack']:
    from haystack.query import SearchQuerySet

    def __len__(self):
        if not self._result_count:
            self._result_count = self.query.get_count()

            # Some backends give weird, false-y values here. Convert to zero.
            if not self._result_count:
                self._result_count = 0

        # This needs to return the actual number of hits, not what's in the
        # cache.
        return max(0, self._result_count - self._ignored_result_count)

    SearchQuerySet.__len__ = __len__


class DataSearchMixin(models.Manager):
    def _haystack_search(self, content, queryset, max_results, partial, using):
        from haystack.query import RelatedSearchQuerySet
        from haystack.inputs import AutoQuery

        if content.strip() == '':
            return RelatedSearchQuerySet().none()

        # Limit to the model bound to this manager, e.g. DataConcept.
        # `load_all` ensures a single database hit when loading the objects
        # that match
        sqs = RelatedSearchQuerySet().models(self.model).load_all()

        # If a non-default backend is being used, set which backend is to
        # be used.
        if using is not None:
            sqs = sqs.using(using)

        if partial:
            # Autocomplete only works with N-gram fields.
            sqs = sqs.autocomplete(text_auto=content)
        else:
            # Automatically handles advanced search syntax for negations
            # and quoted strings.
            sqs = sqs.filter(text=AutoQuery(content))

        if queryset is not None:
            sqs = sqs.load_all_queryset(self.model, queryset)

        if max_results:
            return sqs[:max_results]

        return sqs

    def _basic_search(self, content, queryset):
        """Provides the most basic search possible for the Data* models.

        Individual managers must override this method to actually implement
        the basic search across the pertinent fields for the specific Data*
        model.
        """
        raise NotImplemented('Subclasses must define this method.')

    def search(self, content, queryset=None, max_results=None, partial=False,
               using=None):
        if dep_supported('haystack'):
            return self._haystack_search(content=content,
                                         queryset=queryset,
                                         max_results=max_results,
                                         partial=partial,
                                         using=using)

        return self._basic_search(content, queryset)


class DataFieldSearchMixin(DataSearchMixin):
    def _basic_search(self, content, queryset):
        if queryset is None:
            queryset = self.model.objects.all()

        if content.strip() == '':
            return queryset.none()

        q = Q(name__icontains=content) | \
            Q(description__icontains=content) | \
            Q(keywords__icontains=content) | \
            Q(model_name__icontains=content) | \
            Q(category__name__icontains=content) | \
            Q(category__description__icontains=content) | \
            Q(category__keywords__icontains=content)

        return queryset.filter(q)


class DataConceptSearchMixin(DataSearchMixin):
    def _basic_search(self, content, queryset):
        if queryset is None:
            queryset = self.model.objects.all()

        q = Q(name__icontains=content) | \
            Q(description__icontains=content) | \
            Q(keywords__icontains=content) | \
            Q(fields__name__icontains=content) | \
            Q(fields__description__icontains=content) | \
            Q(fields__keywords__icontains=content) | \
            Q(category__name__icontains=content) | \
            Q(category__description__icontains=content) | \
            Q(category__keywords__icontains=content)

        return queryset.filter(q)


class DataFieldQuerySet(PublishedQuerySet):
    def published(self, user=None, perm='avocado.view_datafield'):
        """Fields can be restricted to one or more sites, so the published
        method is extended to support filtering by site.
        """
        published = super(DataFieldQuerySet, self).published()

        # All published concepts associated with the current site
        # (or no site)
        sites = Q(sites=None) | Q(sites__id=djsettings.SITE_ID)
        published = published.filter(sites)

        if user and settings.PERMISSIONS_ENABLED is not False:
            if OPTIONAL_DEPS['guardian']:
                from guardian.shortcuts import get_objects_for_user

                published = get_objects_for_user(user, perm, published)
            elif settings.PERMISSIONS_ENABLED is True:
                raise ImproperlyConfigured('django-guardian must be installed '
                                           'to use the permissions system')

        return published.distinct()


class DataConceptQuerySet(PublishedQuerySet):
    def published(self, user=None, perm='avocado.view_datafield'):
        """Concepts can be restricted to one or more sites, so the published
        method is extended to support filtering by site. In addition, concepts
        should not be visible if their associated fields are not all available.
        Also, concepts with an unpublished category are not visible. Finally,
        concepts with no fields are not considered visible.
        """
        published = super(DataConceptQuerySet, self).published()

        # All published concepts associated with the current site
        # (or no site)
        sites = Q(sites=None) | Q(sites__id=djsettings.SITE_ID)
        published = published.filter(sites)

        # All published concepts with a non-empty category must have the
        # category published as well in order for it to be visible.
        category_published = Q(category=None) | Q(category__published=True)
        published = published.filter(category_published)

        # Concepts that contain at least one unpublished or archived datafield
        # are removed from the set to prevent exposing unprepared data
        from avocado.models import DataField

        fields_q = Q(archived=True) | Q(published=False)

        if user and settings.PERMISSIONS_ENABLED is not False:
            if OPTIONAL_DEPS['guardian']:
                from guardian.shortcuts import get_objects_for_user

                # If a user is specified, they must also have a permission for
                # accessing the data fields. All data fields that the user does
                # NOT have access to must also be removed from the set.
                restricted_fields = DataField.objects\
                    .exclude(pk__in=get_objects_for_user(user, perm))
                fields_q = fields_q | Q(pk__in=restricted_fields)
            elif settings.PERMISSIONS_ENABLED is True:
                raise ImproperlyConfigured('django-guardian must be installed '
                                           'to use the permissions system')

        shadowed = DataField.objects.filter(fields_q)

        concepts = published.exclude(fields__in=shadowed) \
            .exclude(fields=None).distinct()

        return concepts


class DataFieldManagerDescriptor(ManagerDescriptor):
    """Manager descriptor customized to allow for `f.objects` which returns
    a QuerySet of the underlying model objects which DataField represents.
    """
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, type=None):
        if instance and isinstance(instance.field, models.AutoField):
            return instance.model.objects.all()
        return super(DataFieldManagerDescriptor, self).__get__(instance, type)


class DataFieldManager(PublishedManager, DataFieldSearchMixin):
    "Manager for the `DataField` model."

    def contribute_to_class(self, model, name):
        "Override to use custom manager descriptor."
        super(DataFieldManager, self).contribute_to_class(model, name)
        setattr(model, name, DataFieldManagerDescriptor(self))

    def get_query_set(self):
        return DataFieldQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, app_name, model_name=None, field_name=None):
        queryset = self.get_query_set()
        if type(app_name) is int:
            return queryset.get(id=app_name)

        # Extract attributes from model field instance
        if isinstance(app_name, models.Field):
            field = app_name
            opts = field.model._meta
            app_name = opts.app_label
            model_name = opts.module_name
            field_name = field.name

        keys = ['app_name', 'model_name', 'field_name']

        if type(app_name) is list:
            values = app_name
        elif type(app_name) and '.' in app_name:
            values = app_name.split('.')
        else:
            values = [app_name, model_name, field_name]
        return queryset.get(**dict(zip(keys, values)))


class DataConceptManager(PublishedManager, DataConceptSearchMixin):
    "Manager for the `DataConcept` model."
    def get_query_set(self):
        return DataConceptQuerySet(self.model, using=self._db)

    @transaction.commit_on_success
    def create_from_field(self, field, save=True, **kwargs):
        """Derives a DataConcept from this DataField's descriptors. Additional
        keyword arguments can be passed in to customize the new DataConcept
        object. The DataConcept can also be optionally saved by setting the
        `save` flag.
        """
        for key, value, in field.descriptors.iteritems():
            kwargs.setdefault(key, value)

        concept = self.model(**kwargs)

        if save:
            from avocado.models import DataConceptField
            concept.save()
            cfield = DataConceptField(field=field, concept=concept)
            concept.concept_fields.add(cfield)
        return concept


class DataCategoryManager(PublishedManager):
    "Manager for the `DataCategory` model."


class DataClassBaseManager(models.Manager):
    def get_default_template(self):
        try:
            return self.get_query_set().get(default=True, template=True)
        except self.model.DoesNotExist:
            pass


class DataViewManager(DataClassBaseManager):
    "Manager for the `DataView` model."


class DataContextManager(DataClassBaseManager):
    "Manager for the `DataContext` model."


class DataQueryManager(DataClassBaseManager):
    "Manager for the `DataQuery` model."

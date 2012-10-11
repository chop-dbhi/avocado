from django.db import models
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.db.models.manager import ManagerDescriptor
from django.core.exceptions import ImproperlyConfigured
from avocado.conf import OPTIONAL_DEPS, requires_dep
from avocado.core.managers import PublishedManager, PublishedQuerySet


class DataFieldQuerySet(PublishedQuerySet):
    def published(self, user=None, perm='avocado.view_datafield'):
        """Fields can be restricted to one or more sites, so the published
        method is extended to support filtering by site.
        """
        published = super(DataFieldQuerySet, self).published()

        # Remove internal
        published = published.exclude(internal=True)

        # All published concepts associated with the current site
        # (or no site)
        sites = Q(sites=None) | Q(sites__id=settings.SITE_ID)
        published = published.filter(sites)

        if user:
            if not OPTIONAL_DEPS['guardian']:
                raise ImproperlyConfigured('django-guardian must installed ' \
                    'for object-level permissions.')
            from guardian.shortcuts import get_objects_for_user
            published = get_objects_for_user(user, perm, published)
        return published.distinct()


class DataConceptQuerySet(PublishedQuerySet):
    def published(self, user=None, perm='avocado.view_datafield'):
        """Concepts can be restricted to one or more sites, so the published
        method is extended to support filtering by site. In addition, concepts
        should not be visible if their associated fields are not all available.
        """
        published = super(DataConceptQuerySet, self).published()

        # Remove internal
        published = published.exclude(internal=True)

        # All published concepts associated with the current site
        # (or no site)
        sites = Q(sites=None) | Q(sites__id=settings.SITE_ID)
        published = published.filter(sites)

        # Concepts that contain at least one unpublished or archived datafield
        # are removed from the set to prevent exposing unprepared data
        from avocado.models import DataField
        fields_q = Q(archived=True) | Q(published=False)
        if user:
            if not OPTIONAL_DEPS['guardian']:
                raise ImproperlyConfigured('django-guardian must installed ' \
                    'for object-level permissions.')
            from guardian.shortcuts import get_objects_for_user
            # If a user is specified, they must also have a permission for
            # accessing the data fields. All data fields that the user does
            # NOT have access to must also be removed from the set.
            restricted_fields = DataField.objects\
                .exclude(pk__in=get_objects_for_user(user, perm))
            fields_q = fields_q | Q(pk__in=restricted_fields)

        shadowed = DataField.objects.filter(fields_q)
        concepts = published.exclude(fields__in=shadowed).distinct()
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


class DataFieldManager(PublishedManager):
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
            datafield = queryset.get(id=app_name)
        else:
            keys = ['app_name', 'model_name', 'field_name']
            if type(app_name) is list:
                values = app_name
            elif type(app_name) and '.' in app_name:
                values = app_name.split('.')
            else:
                values = [app_name, model_name, field_name]
            datafield = queryset.get(**dict(zip(keys, values)))
        return datafield

    @requires_dep('haystack')
    def search(self, content, queryset=None, max_results=10):
        from haystack.query import RelatedSearchQuerySet
        sqs = RelatedSearchQuerySet().models(self.model).load_all()\
            .auto_query(content)
        if queryset is not None:
            sqs = sqs.load_all_queryset(self.model, queryset)
        if max_results:
            return sqs[:max_results]
        return sqs


class DataConceptManager(PublishedManager):
    "Manager for the `DataConcept` model."
    def get_query_set(self):
        return DataConceptQuerySet(self.model, using=self._db)

    @requires_dep('haystack')
    def search(self, content, queryset=None, max_results=10):
        from haystack.query import RelatedSearchQuerySet
        sqs = RelatedSearchQuerySet().models(self.model).load_all()\
            .auto_query(content)
        if queryset is not None:
            sqs = sqs.load_all_queryset(self.model, queryset)
        if max_results:
            return sqs[:max_results]
        return sqs

    @transaction.commit_on_success
    def create_from_field(self, datafield, save=True, **kwargs):
        """Derives a DataConcept from this DataField's descriptors. Additional
        keyword arguments can be passed in to customize the new DataConcept
        object. The DataConcept can also be optionally saved by setting the
        `save` flag.
        """
        for key, value, in datafield.descriptors.iteritems():
            kwargs.setdefault(key, value)

        concept = self.model(**kwargs)

        if save:
            from avocado.models import DataConceptField
            concept.save()
            cfield = DataConceptField(field=datafield, concept=concept)
            concept.concept_fields.add(cfield)
        return concept


class DataCategoryManager(PublishedManager):
    "Manager for the `DataCategory` model."

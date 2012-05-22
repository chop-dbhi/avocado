from django.db.models import Q
from django.db import transaction
from django.conf import settings
from haystack.query import RelatedSearchQuerySet
from avocado.core.cache import CacheQuerySet
from avocado.core.managers import PassThroughManager

SITES_APP_INSTALLED = 'django.contrib.sites' in settings.INSTALLED_APPS


class PublishedQuerySet(CacheQuerySet):
    "Adds additional helper methods focused around access and permissions."
    def published(self):
        "Returns all published non-archived objects."
        return self.filter(published=True, archived=False)


class PublishedManager(PassThroughManager):
    def get_query_set(self):
        return PublishedQuerySet(self.model, using=self._db)


class DataFieldQuerySet(PublishedQuerySet):
    def published(self):
        """Fields can be restricted to one or more sites, so the published
        method is extended to support filtering by site.
        """
        published = super(DataFieldQuerySet, self).published()

        if SITES_APP_INSTALLED:
            # All published concepts associated with the current site
            # (or no site)
            sites = Q(sites=None) | Q(sites__id=settings.SITE_ID)
            published = published.filter(sites)
        return published.distinct()


class DataConceptQuerySet(PublishedQuerySet):
    def published(self):
        """Concepts can be restricted to one or more sites, so the published
        method is extended to support filtering by site. In addition, concepts
        should not be visible if their associated fields are not all available.
        """
        published = super(DataConceptQuerySet, self).published()

        if SITES_APP_INSTALLED:
            # All published concepts associated with the current site
            # (or no site)
            sites = Q(sites=None) | Q(sites__id=settings.SITE_ID)
            published = published.filter(sites)
        # Concepts that contain at least one non-published datafields are
        # removed from the set to prevent exposing non-prepared data
        fields = Q(fields__published=False) | Q(fields__archived=True)
        shadowed = self.filter(fields)

        return published.exclude(pk__in=shadowed).distinct()


class DataFieldManager(PublishedManager):
    "Manager for the `DataField` model."
    def get_query_set(self):
        return DataFieldQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, app_name, model_name=None, field_name=None):
        queryset = self.get_query_set()
        if type(app_name) is int:
            datafield = queryset.get(id=app_name)
        else:
            keys = ['app_name', 'model_name', 'field_name']
            if type(app_name) is str:
                if not model_name:
                    values = app_name.split('.')
                else:
                    values = [app_name, model_name, field_name]
            elif type(app_name) is list:
                values = app_name
            datafield = queryset.get(**dict(zip(keys, values)))
        return datafield

    def search(self, content, queryset=None, max_results=10):
        sqs = RelatedSearchQuerySet().models(self.model).load_all().auto_query(content)
        if queryset is not None:
            sqs = sqs.load_all_queryset(self.model, queryset)
        if max_results:
            return sqs[:max_results]
        return sqs


class DataConceptManager(PassThroughManager):
    "Manager for the `DataConcept` model."
    def get_query_set(self):
        return DataConceptQuerySet(self.model, using=self._db)

    def search(self, content, queryset=None, max_results=10):
        sqs = RelatedSearchQuerySet().models(self.model).load_all().auto_query(content)
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

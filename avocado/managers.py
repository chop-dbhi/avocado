from django.db.models import Q
from django.db import transaction
from django.conf import settings
from avocado.core.cache import CacheManager
from avocado.core.managers import PassThroughManager

SITES_APP_INSTALLED = 'django.contrib.sites' in settings.INSTALLED_APPS

class PublishedManager(PassThroughManager, CacheManager):
    use_for_related_fields = True

    def published(self):
        "Returns all published datafields."
        return self.get_query_set().filter(published=True, archived=False)


class FieldManager(PublishedManager):
    "Adds additional helper methods focused around access and permissions."
    def get_by_natural_key(self, app_name, model_name, field_name):
        return self.get_query_set().get(
            app_name=app_name,
            model_name=model_name,
            field_name=field_name
        )


class ConceptManager(PublishedManager):

    def published(self):
        queryset = self.get_query_set()

        if SITES_APP_INSTALLED:
            # All published concepts associated with a category and associated with
            # the current site (or no site)
            sites = Q(sites=None) | Q(sites__id=settings.SITE_ID)
        else:
            sites = Q()

        published = queryset.filter(sites, published=True, archived=False)
        # Concepts that contain at least one non-published datafields are removed from
        # the set to prevent exposing non-prepared data
        shadowed = queryset.filter(fields__published=False)

        return published.exclude(pk__in=shadowed).distinct()

    @transaction.commit_on_success
    def create_from_field(self, datafield, save=False, **kwargs):
        """Derives a DataConcept from this DataField's descriptors. Additional
        keyword arguments can be passed in to customize the new DataConcept object.
        The DataConcept can also be optionally saved by setting the ``save`` flag.
        """
        for k, v, in datafield.descriptors.iteritems():
            kwargs.setdefault(k, v)

        concept = self.model(**kwargs)

        if save:
            from avocado.models import ConceptField
            concept.save()
            cfield = ConceptField(datafield=datafield, concept=concept)
            concept.concept_fields.add(cfield)
        return concept


class CategoryManager(PublishedManager):
    pass

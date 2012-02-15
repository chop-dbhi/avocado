from django.db.models import Q
from django.db import transaction
from django.conf import settings
from avocado.core.managers import PassThroughManager
from avocado.models import ConceptField

class FieldManager(PassThroughManager):
    "Adds additional helper methods focused around access and permissions."
    use_for_related_fields = True

    def get_by_natural_key(self, app_name, model_name, field_name):
        return self.get_query_set().get(
            app_name=app_name,
            model_name=model_name,
            field_name=field_name
        )

    def published(self):
        "Returns all published fields."
        return self.get_query_set().filter(published=True, archived=False)


class ConceptManager(PassThroughManager):
    use_for_related_fields = True

    def published(self):
        queryset = self.get_query_set()
        # All published concepts associated with a domain and associated with
        # the current site (or no site)
        sites = Q(sites=None) | Q(sites__id=settings.SITE_ID)
        published = queryset.filter(sites, published=True, archived=False,
            domain__isnull=False)
        # Concepts that contain at least one non-published fields are removed from
        # the set
        shadowed = queryset.filter(fields__published=False)

        return published.exclude(pk__in=shadowed)\
            .filter(published__in=published).distinct()

    @transaction.commit_on_success
    def create_from_field(self, field, save=False, **kwargs):
        """Derives a Concept from this Field's descriptors. Additional
        keyword arguments can be passed in to customize the new Concept object.
        The Concept can also be optionally saved by setting the ``save`` flag.
        """
        for k, v, in field.descriptors.iteritems():
            kwargs.setdefault(k, v)

        concept = self.model(**kwargs)

        if save:
            concept.save()
            cfield = ConceptField(field=field, concept=concept)
            concept.concept_fields.add(cfield)
        return concept


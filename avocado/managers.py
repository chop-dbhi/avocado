from django.db import models
from django.db.models import Q
from django.conf import settings

class FieldManager(models.Manager):
    "Adds additional helper methods focused around access and permissions."
    use_for_related_fields = True

    def _get_for_site(self):
        return Q(sites=None) | Q(sites__id__exact=settings.SITE_ID)

    def _public_for_auth_user(self, user):
        kwargs = {'published': True}
        groups = Q(group=None) | Q(group__in=user.groups.all())
        sites = self._get_for_site()

        return self.get_query_set().filter(sites, groups, **kwargs).distinct()

    def _public_for_anon_user(self):
        kwargs = {
            'group': None,
            'published': True
        }
        sites = self._get_for_site()

        return self.get_query_set().filter(sites, **kwargs).distinct()

    def get_by_natural_key(self, app_name, model_name, field_name):
        return self.get_query_set().get(app_name=app_name, model_name=model_name,
            field_name=field_name)

    def public(self, user=None):
        "Returns all publically available fields given a user."
        if user and user.is_authenticated():
            return self._public_for_auth_user(user)
        return self._public_for_anon_user()


class ConceptManager(models.Manager):
    def _get_not_for_site(self):
        return Q(fields__sites__isnull=False) & ~Q(fields__sites__exact=settings.SITE_ID)

    def _public_for_auth_user(self, user):
        groups = list(user.groups.all())
        # resolve groups to take a length; this will greatly reduce
        # the complexity of the later query
        if len(groups) == 0:
            return self._public_for_anon_user()

        queryset = self.get_query_set()
        # all public columns
        public = queryset.filter(published=True, domain__isnull=False)
        # columns that contain at least one non-public field
        shadowed = queryset.filter(fields__published=False)
        # columns that contain fields associated with a group
        grouped = queryset.filter(Q(fields__group__isnull=False) & \
            ~Q(fields__group__in=groups))
        # columns that are not in the current site (or not associated with
        # a site)
        sites = queryset.filter(self._get_not_for_site())

        return public.exclude(pk__in=shadowed).exclude(pk__in=grouped)\
            .exclude(pk__in=sites).distinct()

    def _public_for_anon_user(self):
        queryset = self.get_query_set()
        # all public columns
        public = queryset.filter(published=True, domain__isnull=False)
        # columns that contain at least one non-public field
        shadowed = queryset.filter(fields__published=False)
        # columns that contain fields associated with a group
        grouped = queryset.filter(fields__group__isnull=False)
        # columns that are not in the current site (or not associated with
        # a site)
        sites = queryset.filter(self._get_not_for_site())

        return public.exclude(pk__in=shadowed).exclude(pk__in=grouped)\
            .exclude(pk__in=sites).distinct()

    def public(self, user=None):
        "Returns all publically available fields given a user."
        if user and user.is_authenticated():
            return self._public_for_auth_user(user)
        return self._public_for_anon_user()

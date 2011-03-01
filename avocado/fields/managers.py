from django.db import models
from django.db.models import Q
from django.conf import settings

class FieldManager(models.Manager):
    "Adds additional helper methods focused around access and permissions."
    use_for_related_fields = True

    def get_by_natural_key(self, app_name, model_name, field_name):
        return self.get_query_set().get(app_name=app_name, model_name=model_name,
            field_name=field_name)

    def _get_for_site(self):
        return Q(sites=None) | Q(sites__id__exact=settings.SITE_ID)

    def _public_for_auth_user(self, user):
        kwargs = {'is_public': True}
        groups = Q(group=None) | Q(group__in=user.groups.all())
        sites = self._get_for_site()

        return self.get_query_set().filter(sites, groups, **kwargs).distinct()

    def _public_for_anon_user(self):
        kwargs = {
            'group': None,
            'is_public': True
        }
        sites = self._get_for_site()

        return self.get_query_set().filter(sites, **kwargs).distinct()

    def public(self, user=None):
        "Returns all publically available fields given a user."
        if user and user.is_authenticated():
            return self._public_for_auth_user(user)
        return self._public_for_anon_user()

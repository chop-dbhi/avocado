import re

from django.db import models, database
from django.db.models import Q
from django.utils import stopwords
from django.conf import settings

from avocado.concepts import db

BACKEND = database['ENGINE'].split('.')[-1]

def _tokenize(search_str):
    "Strips stopwords and tokenizes search string if not already a list."
    if isinstance(search_str, basestring):
        # TODO determine appropriate characters that should be retained
        sanitized_str = re.sub('[^\w\s]+', '', search_str)
        cleaned_str = stopwords.strip_stopwords(sanitized_str)
        toks = cleaned_str.split()
    else:
        toks = list(search_str)
    return toks

class ConceptManager(models.Manager):
    use_for_related_fields = True

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
        public = queryset.filter(is_public=True, category__isnull=False)
        # columns that contain at least one non-public field
        shadowed = queryset.filter(fields__is_public=False)
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
        public = queryset.filter(is_public=True, category__isnull=False)
        # columns that contain at least one non-public field
        shadowed = queryset.filter(fields__is_public=False)
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

    def fulltext_search(self, search_str, base_queryset=None, use_icontains=False):
        """Performs a fulltext search provided the database backend supports
        fulltext searching. Two optional parameters include:

            `base_queryset' - a starting queryset to perform the search on

            `use_icontains' - a boolean for whether to fallback to the
                `icontains_search' if no hits are found using fulltext

        TODO update to take in account different database backends
        """
        if base_queryset is None:
            base_queryset = self.get_query_set()

        toks = _tokenize(search_str)

        func = getattr(db, BACKEND, None)

        # if fulltext search is supported, generate queryset
        if func:
            queryset = func(base_queryset, toks)

        # if fulltext is not supported or not hits are found, run the
        # icontains operator
        if func is None or (use_icontains and not queryset.exists()):
            queryset = self.icontains_search(toks, base_queryset.all())

        return queryset

    def icontains_search(self, search_str, base_queryset=None):
        """Performs an AND'ed icontains search. This is not the preferred
        search method since this can be very expensive. This should act as
        a fallback if the `fulltext_search' does not produce any results.
        """
        if base_queryset is None:
            queryset = self.get_query_set()
        else:
            queryset = base_queryset.all()

        toks = _tokenize(search_str)

        for t in toks:
            queryset = queryset.filter(search_doc__icontains=t)

        return queryset

import re

from django.db import models
from django.db.models.query import QuerySet
from django.utils import stopwords

from avocado.conf import settings

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

    def public(self, sql):
        """Translates to::

            'return all concepts which are public, all fields associated with
            them are public and all fields are not part of a group.'
        """
        ids = [x.id for x in self.raw(sql)]
        return self.get_query_set().filter(id__in=ids)

    if settings.FIELD_GROUP_PERMISSIONS:
        def restrict_by_group(self, sql, groups):
            """Translates to::

                'return all concepts which are public, all fields associated with
                them are public and all fields per column are either not part of
                a group or are within any of the groups specified by ``groups``.
            """

            if isinstance(groups, QuerySet):
                groups = groups.order_by().values_list('id', flat=True)
            ids = [x.id for x in self.raw(sql, params=(tuple(groups),))]
            return self.get_query_set().filter(id__in=ids)

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

        column = '"%s"."search_tsv"' % self.model._meta.db_table

        toks = _tokenize(search_str)

        if not toks:
            return base_queryset

        tok_str = '&'.join(toks)

        queryset = base_queryset.extra(where=(column + ' @@ to_tsquery(%s)',),
            params=(tok_str,))

        if use_icontains and not queryset.exists():
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

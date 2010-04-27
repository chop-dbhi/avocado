import re

from django.db import models
from django.db.models import Q
from django.utils import stopwords

def tokenize_search_str(search_str):
    "Strips stopwords and tokenizes search string if not already a list."
    if isinstance(search_str, basestring):
        # TODO determine appropriate characters that should be retained
        cleaned_str = re.sub('[^\w\s@-]+', '', search_str)
        tok_str = stopwords.strip_stopwords(cleaned_str)
        toks = tok_str.split()
    else:
        toks = list(search_str)

    return toks


class ConceptManager(models.Manager):
    def public(self, *args, **kwargs):
        return self.get_query_set().filter(*args, is_public=True, **kwargs)

    def restrict_by_group(self, groups):
        """Returns public concepts that are apart of the specified groups or
        none at all.
        """
        return self.public(Q(groups__isnull=True) |
            Q(groups__in=groups)).distinct()

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

        toks = tokenize_search_str(search_str)
        tok_str = '&'.join(toks)

        queryset = base_queryset.extra(where=('search_tsv @@ to_tsquery(%s)',),
            params=(tok_str,))

        # TODO for django 1.2, update to use .exists()
        if use_icontains and queryset.count() == 0:
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

        toks = tokenize_search_str(search_str)

        for t in toks:
            queryset = queryset.filter(search_doc__icontains=t)

        return queryset

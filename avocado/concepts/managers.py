import re

from django.db import models
from django.utils import stopwords

from avocado.conf import settings

class ConceptManager(models.Manager):
    use_for_related_fields = True
    
    def _tokenize(self, search_str):
        "Strips stopwords and tokenizes search string if not already a list."
        if isinstance(search_str, basestring):
            # TODO determine appropriate characters that should be retained
            sanitized_str = re.sub('[^\w\s@-]+', '', search_str)
            cleaned_str = stopwords.strip_stopwords(sanitized_str)
            toks = cleaned_str.split()
        else:
            toks = list(search_str)
        return toks

    def public(self, *args, **kwargs):
        return self.get_query_set().filter(*args, is_public=True, **kwargs)

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

        toks = self._tokenize(search_str)
        tok_str = '&'.join(toks)

        queryset = base_queryset.extra(where=('search_tsv @@ to_tsquery(%s)',),
            params=(tok_str,))

        if use_icontains and queryset.exists():
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

        toks = self._tokenize(search_str)

        for t in toks:
            queryset = queryset.filter(search_doc__icontains=t)

        return queryset

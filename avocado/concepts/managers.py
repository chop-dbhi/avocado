from django.db import models
from django.db.models import Q
from django.utils import stopwords

class ConceptManager(models.Manager):
    def public(self, *args, **kwargs):
        return self.get_query_set().filter(*args, is_public=True, **kwargs)

    def restrict_by_group(self, groups):
        """Returns public concepts that are apart of the specified groups or
        none at all.
        """
        return self.public(Q(groups__isnull=True) |
            Q(groups__in=groups)).distinct()

    def fulltext(self, search_str, base_queryset=None):
        if base_queryset is None:
            base_queryset = self.get_query_set()
        
        search_str = stopwords.strip_stopwords(search_str)
        toks = search_str.split()
        tok_str = '&'.join(toks)

        queryset = base_queryset.extra(where=('search_hash @@ to_tsquery(%s)',),
            params=(tok_str,))

        # fallback if the fulltext doesn't return anything
        if queryset.count() == 0:
            queryset = base_queryset.all()
            for t in toks:
                queryset = queryset.filter(search_doc__icontains=t)
        return queryset
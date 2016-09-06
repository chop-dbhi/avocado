from django.db.models.query import EmptyQuerySet
from django.utils.importlib import import_module
from modeltree.tree import trees
from avocado.formatters import RawFormatter
from avocado.conf import settings


QUERY_PROCESSOR_DEFAULT_ALIAS = 'default'


class QueryProcessor(object):
    """Prepares and builds a QuerySet for export.

    Overriding or extending these methods enable customizing the behavior
    pre/post-construction of the query.
    """
    def __init__(self, context=None, view=None, tree=None, include_pk=True):
        self.context = context
        self.view = view
        self.tree = tree
        self.include_pk = include_pk

    def get_queryset(self, queryset=None, **kwargs):
        """Returns a queryset with the context and view and view applied.

        Serrano and Avocado pass the Django request object as the `request`
        keyword argument, so custom sub-classes of QueryProcessor can modify
        the query based on request-related data such as the user.
        """
        if self.context:
            queryset = self.context.apply(queryset=queryset, tree=self.tree)

        if self.view:
            queryset = self.view.apply(queryset=queryset, tree=self.tree,
                                       include_pk=self.include_pk)

        if queryset is None:
            queryset = trees[self.tree].get_queryset()

        return queryset

    def get_exporter(self, klass, **kwargs):
        """Prepares and returns an exporter for the bound view.

        If include_pk is true, a raw formatter is prepended to handle the
        primary key value.
        """
        exporter = klass(self.view)

        if self.include_pk:
            pk_name = trees[self.tree].root_model._meta.pk.name
            exporter.add_formatter(RawFormatter, keys=[pk_name], index=0)

        return exporter

    def get_iterable(self, offset=None, limit=None, queryset=None, **kwargs):
        "Returns an iterable that can be used by an exporter."
        if queryset is None:
            queryset = self.get_queryset(**kwargs)

        # Empty querysets are not propagated to the internal query object in
        # Django 1.5 and below. This ensures the result set is in fact empty.
        if isinstance(queryset, EmptyQuerySet):
            return iter(())

        if offset and limit:
            queryset = queryset[offset:offset + limit]
        elif offset:
            queryset = queryset[offset:]
        elif limit:
            queryset = queryset[:limit]

        compiler = queryset.query.get_compiler(queryset.db)

        return compiler.results_iter()


class QueryProcessors(object):
    def __init__(self, processors):
        self.processors = processors
        self._processors = {}

    def __getitem__(self, key):
        return self._get(key)

    def __len__(self):
        return len(self._processors)

    def __nonzero__(self):
        return True

    def _get(self, key):
        # Import class if not cached
        if key not in self._processors:
            toks = self.processors[key].split('.')
            klass_name = toks.pop()
            path = '.'.join(toks)
            klass = getattr(import_module(path), klass_name)
            self._processors[key] = klass
        return self._processors[key]

    def __iter__(self):
        return iter(self.processors)

    @property
    def default(self):
        return self[QUERY_PROCESSOR_DEFAULT_ALIAS]


query_processors = QueryProcessors(settings.QUERY_PROCESSORS)

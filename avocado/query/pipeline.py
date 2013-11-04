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
        "Returns a queryset based on the context and view."
        if self.context:
            queryset = \
                self.context.apply(queryset=queryset, tree=self.tree)

        if self.view:
            queryset = self.view.apply(queryset=queryset, tree=self.tree,
                                       include_pk=self.include_pk)

        if queryset is None:
            queryset = trees[self.tree].get_queryset().values('pk')

        return queryset

    def get_exporter(self, klass, **kwargs):
        "Returns an exporter prepared for the queryset."
        exporter = klass(self.view)

        if self.include_pk:
            pk_name = trees[self.tree].root_model._meta.pk.name
            exporter.add_formatter(RawFormatter(keys=[pk_name]), index=0)

        return exporter

    def get_iterable(self, offset=None, limit=None, **kwargs):
        "Returns an iterable that can be used by an exporter."
        queryset = self.get_queryset(**kwargs)

        if offset is not None and limit is not None:
            queryset = queryset[offset:offset + limit]
        elif offset is not None:
            queryset = queryset[offset:]
        elif limit is not None:
            queryset = queryset[:limit]

        # ModelTreeQuerySet has a raw method defined, but fallback
        # to the creating a results iter if not present.
        if hasattr(queryset, 'raw'):
            iterable = queryset.raw()
        else:
            compiler = queryset.query.get_compiler(queryset.db)
            iterable = compiler.results_iter()

        return iterable


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

    @property
    def default(self):
        return self[QUERY_PROCESSOR_DEFAULT_ALIAS]


query_processors = QueryProcessors(settings.QUERY_PROCESSORS)

from modeltree.query import ModelTreeQuerySet

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class BaseExporter(object):
    "Base class for all exporters"

    preferred_formats = []

    def __init__(self, queryset, concepts):
        if not isinstance(queryset, ModelTreeQuerySet):
            queryset = queryset._clone(klass=ModelTreeQuerySet)

        self.queryset = queryset
        self.concepts = concepts

    def _get_raw_query(self, concepts):
        fields = []
        for c in concepts:
            cfields = c.conceptfields.select_related('field')
            fields.extend([cfield.field.field for cfield in cfields])
        return self.queryset.select(*fields, inclue_pk=False)

    def _read_row(self, row, formatters):
        for i, (c, f) in enumerate(formatters):
            data, row = row[:f.length], row[f.length:]
            values = c.get_formatter_values(data)
            yield f(values, c, self.preferred_formats)

    def read(self, concepts=None):
        concepts = concepts or self.concepts
        # cache each concept formatter a head of time
        formatters = [(x, x.get_formatter()) for x in concepts]

        for row in iter(self._get_raw_query(concepts)):
            yield self._read_row(row, formatters)

    def export(self, *args, **kwargs):
        raise NotImplemented

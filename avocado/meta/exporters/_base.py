from modeltree.query import ModelTreeQuerySet
from avocado.meta.formatters import registry

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

    def _get_raw_query(self, fields):
        return self.queryset.select(*fields, inclue_pk=False)

    def _read_row(self, row, params):
        for i, (keys, length, formatter) in enumerate(params):
            part, row = row[:length], row[length:]
            values = OrderedDict(zip(keys, part))
            yield formatter(values, self.preferred_formats)

    def _get_keys(self, fields):
        return [f.field_name for f in fields]

    def read(self, concepts=None):
        concepts = concepts or self.concepts
        params = []
        select_fields = []

        for concept in concepts:
            cfields = concept.conceptfields.select_related('field')
            fields = [c.field for c in cfields]
            select_fields.extend(f.field for f in fields)
            formatter = registry[concept.formatter](cfields)
            params.append((self._get_keys(fields), len(cfields), formatter))

        for row in iter(self._get_raw_query(select_fields)):
            yield self._read_row(row, params)

    def export(self, *args, **kwargs):
        raise NotImplemented

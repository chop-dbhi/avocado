from modeltree.query import ModelTreeQuerySet
from avocado.formatters import registry

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

    def _get_rows(self, fields):
        return self.queryset.select(*fields, inclue_pk=False)

    def _format_row(self, row, params):
        for i, (keys, length, formatter) in enumerate(params):
            part, row = row[:length], row[length:]
            values = OrderedDict(zip(keys, part))
            yield formatter(values, self.preferred_formats)

    def _get_keys(self, fields):
        # Best case scenario, no conflicts, return as is. Otherwise
        # duplicates found will be suffixed with a '_N' where N is the
        # occurred position.
        keys = [f.field_name for f in fields]

        if len(set(keys)) != len(fields):
            cnts = {}
            for i, key in enumerate(keys):
                if keys.count(key) > 1:
                    cnts.setdefault(key, 0)
                    keys[i] = '{}_{}'.format(key, cnts[key])
                    cnts[key] += 1
        return keys

    def read(self, concepts=None):
        concepts = concepts or self.concepts
        params = []
        select_fields = []

        for concept in concepts:
            cfields = concept.concept_fields.select_related('datafield')
            fields = [c.datafield for c in cfields]
            select_fields.extend(f.field for f in fields)
            formatter = registry[concept.formatter](concept)
            params.append((self._get_keys(fields), len(cfields), formatter))

        for row in iter(self._get_rows(select_fields)):
            yield self._format_row(row, params)

    def write(self, *args, **kwargs):
        raise NotImplemented

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.db.models.query import QuerySet
from avocado.formatters import registry as formatters


class BaseExporter(object):
    "Base class for all exporters"

    preferred_formats = []

    def __init__(self, concepts):
        if isinstance(concepts, QuerySet):
            concepts = concepts.prefetch_related('concept_fields__field')
        self.concepts = concepts
        self.params = []

        for concept in concepts:
            cfields = concept.concept_fields.select_related('field')
            fields = [c.field for c in cfields]
            formatter = formatters[concept.formatter](concept)
            self.params.append((self._get_keys(fields), len(cfields), formatter))

    def _format_row(self, row):
        for keys, length, formatter in self.params:
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

    def read(self, iterable):
        "Takes an iterable that produces rows to be formatted."
        for row in iterable:
            yield self._format_row(row)

    def write(self, iterable, *args, **kwargs):
        raise NotImplemented

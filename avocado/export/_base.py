from cStringIO import StringIO


class BaseExporter(object):
    "Base class for all exporters"

    preferred_formats = []

    def __init__(self, concepts):
        self.concepts = concepts
        self.params = []

        for concept in concepts:
            length = concept.concept_fields.count()
            self.params.append((concept.format, length))

    def get_file_obj(self, name):
        if name is None:
            return StringIO()
        if isinstance(name, basestring):
            return open(name, 'w+')
        return name

    def _format_row(self, row):
        for formatter, length in self.params:
            values, row = row[:length], row[length:]
            yield formatter(values, self.preferred_formats)

    def read(self, iterable):
        "Takes an iterable that produces rows to be formatted."
        for row in iterable:
            yield self._format_row(row)

    def write(self, iterable, *args, **kwargs):
        raise NotImplemented

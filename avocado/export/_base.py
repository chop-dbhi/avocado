from cStringIO import StringIO


class BaseExporter(object):
    "Base class for all exporters"
    file_extension = 'txt'
    content_type = 'text/plain'
    preferred_formats = []

    def __init__(self, concepts):
        self.concepts = concepts
        self.params = []
        self.row_length = 0

        for concept in concepts:
            length = concept.concept_fields.count()
            self.row_length += length
            self.params.append((concept.format, length))

    def get_file_obj(self, name=None):
        if name is None:
            return StringIO()
        if isinstance(name, basestring):
            return open(name, 'w+')
        return name

    def _format_row(self, row):
        for formatter, length in self.params:
            values, row = row[:length], row[length:]
            yield formatter(values, self.preferred_formats)

    def read(self, iterable, force_distinct=True, *args, **kwargs):
        """Takes an iterable that produces rows to be formatted.

        If `force_distinct` is true, rows will be filtered based on the slice
        of the row that is *up* for to be formatted. Note, this assumes the
        rows are ordered.
        """
        last_row = None
        for row in iterable:
            _row = row[:self.row_length]
            if force_distinct and _row == last_row:
                continue
            last_row = _row
            yield self._format_row(_row)

    def write(self, iterable, *args, **kwargs):
        raise NotImplemented

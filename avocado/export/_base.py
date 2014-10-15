from avocado.models import DataConcept, DataView
from avocado.formatters import Formatter
from cStringIO import StringIO


class BaseExporter(object):
    "Base class for all exporters"
    file_extension = 'txt'
    content_type = 'text/plain'
    preferred_formats = ()

    def __init__(self, concepts=None):
        if concepts is None:
            concepts = ()
        elif isinstance(concepts, DataView):
            node = concepts.parse()
            concepts = node.get_concepts_for_select()

        self.params = []
        self.row_length = 0
        self.concepts = concepts

        for concept in concepts:
            self.add_formatter(concept)

    def __repr__(self):
        return u'<{0}: {1}/{2}>'.format(self.__class__.__name__,
                                        len(self.params), self.row_length)

    def add_formatter(self, formatter, length=None, index=None):
        if isinstance(formatter, DataConcept):
            length = formatter.concept_fields.count()
            formatter = formatter.format
        elif isinstance(formatter, Formatter):
            length = len(formatter.keys)
        elif length is None:
            raise ValueError('A length must be supplied with the to '
                             'denote how much of the row will be formatted.')

        params = (formatter, length)
        self.row_length += length

        if index is not None:
            self.params.insert(index, params)
        else:
            self.params.append(params)

    def get_file_obj(self, name=None):
        if name is None:
            return StringIO()
        if isinstance(name, basestring):
            return open(name, 'w+')
        return name

    def _format_row(self, row, **kwargs):
        for formatter, length in self.params:
            values, row = row[:length], row[length:]
            yield formatter(values, preferred_formats=self.preferred_formats,
                            **kwargs)

    def read(self, iterable, force_distinct=True, offset=None, limit=None,
             *args, **kwargs):
        """Takes an iterable that produces rows to be formatted.

        If `force_distinct` is true, rows will be filtered based on the slice
        of the row that is going to be formatted.

        If `offset` is defined, only rows that are produced after the offset
        index are returned.

        If `limit` is defined, once the limit has been reached (or the
        iterator is exhausted), the loop will exit.
        """
        emitted = 0
        unique_rows = set()

        for i, row in enumerate(iterable):
            if limit is not None and emitted >= limit:
                break

            _row = row[:self.row_length]

            if force_distinct:
                _row_hash = hash(tuple(_row))

                if _row_hash in unique_rows:
                    continue

                unique_rows.add(_row_hash)

            if offset is None or i >= offset:
                emitted += 1
                yield self._format_row(_row, **kwargs)

    def write(self, iterable, *args, **kwargs):
        for row_gen in self.read(iterable, *args, **kwargs):
            row = []
            for data in row_gen:
                row.extend(data.values())
            yield tuple(row)

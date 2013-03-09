from avocado.models import DataConcept, DataView
from avocado.formatters import Formatter
from cStringIO import StringIO


def get_file_obj(name=None):
    if name is None:
        return StringIO()
    if isinstance(name, basestring):
        return open(name, 'w+')
    return name


class RowFormatter(object):
    def __init__(self, concepts=None, preferred_formats=None):
        if concepts is None:
            concepts = ()
        elif isinstance(concepts, DataView):
            node = concepts.parse()
            concepts = node.get_concepts_for_select()

        self.params = []
        self.preferred_formats = preferred_formats
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

    def __call__(self, row, **kwargs):
        "Apply the formatter for each chunk of the row."
        for formatter, length in self.params:
            values, row = row[:length], row[length:]
            yield formatter(values, preferred_formats=self.preferred_formats, **kwargs)


class Exporter(object):
    "Base class for all exporters"

    file_extension = 'txt'
    content_type = 'text/plain'
    preferred_formats = []

    def __init__(self, iterable, concepts, force_distinct=True, preferred_formats=None, **kwargs):
        """Takes an iterable that produces rows to be formatted.

        If `force_distinct` is true, rows will be filtered based on the slice
        of the row that is *up* for to be formatted. Note, this assumes the
        rows are ordered.
        """
        self.iterator = iter(iterable)
        self.force_distinct = force_distinct
        self.kwargs = kwargs

        self.concepts = concepts
        self.preferred_formats = preferred_formats
        self._format = RowFormatter(concepts, self.preferred_formats)
        self._last_row = None

    def __iter__(self):
        return self

    def next(self):
        while True:
            row = next(self.iterator)

            # Truncate to the processable length
            row = row[:self._format.row_length]

            # Perform a check if force distinct is true, only store the
            # last row if necessary
            if self.force_distinct:
                if row == self._last_row:
                    continue
                self._last_row = row

            return self._format(row, **self.kwargs)

    def write(self, *args, **kwargs):
        raise NotImplemented

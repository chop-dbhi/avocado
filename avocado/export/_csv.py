import csv
from _base import BaseExporter


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    Adapted from https://github.com/jdunck/python-unicodecsv/blob/master/unicodecsv/__init__.py   # noqa
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', *args, **kwds):
        self.encoding = encoding
        self.writer = csv.writer(f, dialect, *args, **kwds)

    def writerow(self, row):
        self.writer.writerow([
            s.encode("utf-8")
            if 'encode' in dir(s) else s
            for s in row
        ])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class CSVExporter(BaseExporter):
    short_name = 'CSV'
    long_name = 'Comma-Separated Values (CSV)'

    file_extension = 'csv'
    content_type = 'text/csv'

    preferred_formats = ('csv', 'string')

    def write(self, iterable, buff=None, *args, **kwargs):
        buff = self.get_file_obj(buff)
        writer = UnicodeWriter(buff, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([f['label'] for f in self.header])

        for row in iterable:
            writer.writerow(row)

        return buff

import csv
from _base import BaseExporter


class CSVExporter(BaseExporter):
    short_name = 'CSV'
    long_name = 'Comma-Separated Values (CSV)'

    file_extension = 'csv'
    content_type = 'text/csv'

    preferred_formats = ('csv', 'number', 'string')

    def write(self, iterable, buff=None, *args, **kwargs):
        header = []
        buff = self.get_file_obj(buff)
        writer = csv.writer(buff, quoting=csv.QUOTE_MINIMAL)

        for i, row_gen in enumerate(self.read(iterable, *args, **kwargs)):
            row = []
            for data in row_gen:
                if i == 0:
                    header.extend(data.keys())
                row.extend(data.values())
            if i == 0:
                writer.writerow(header)
            writer.writerow(row)
        return buff

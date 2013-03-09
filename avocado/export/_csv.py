import csv
from _base import Exporter, get_file_obj


class CSVExporter(Exporter):
    short_name = 'CSV'
    long_name = 'Comma-Separated Values (CSV)'

    file_extension = 'csv'
    content_type = 'text/csv'

    preferred_formats = ('csv', 'number', 'string')

    def write(self, buff=None, *args, **kwargs):
        header = []
        buff = get_file_obj(buff)

        writer = csv.writer(buff, quoting=csv.QUOTE_MINIMAL)

        for i, row_gen in enumerate(self):
            row = []
            for data in row_gen:
                if i == 0:
                    header.extend(data.keys())
                row.extend(data.values())
            if i == 0:
                writer.writerow(header)
            writer.writerow(row)
        return buff

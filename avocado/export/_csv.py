import csv
from _base import BaseExporter


class CSVExporter(BaseExporter):
    file_extension = 'csv'
    preferred_formats = ('number', 'string')

    def write(self, iterable, buff=None):
        header = []
        buff = self.get_file_obj(buff)
        writer = csv.writer(buff, quoting=csv.QUOTE_MINIMAL)

        for i, row_gen in enumerate(self.read(iterable)):
            row = []
            for data in row_gen:
                if i == 0:
                    header.extend(data.keys())
                row.extend(data.values())
            if i == 0:
                writer.writerow(header)
            writer.writerow(row)
        return buff

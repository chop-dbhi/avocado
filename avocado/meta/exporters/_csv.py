import csv
from avocado.meta.exporters._base import BaseExporter

class CSVExporter(BaseExporter):
    preferred_formats = ('number', 'string')

    def export(self, buff):
        """Export to csv method
        `buff` - file-like object that is being written to
        """
        writer = csv.writer(buff, quoting=csv.QUOTE_MINIMAL)

        for i, row_gen in enumerate(self.read()):
            row = []
            for data in row_gen:
                values = data.values()

                # Write headers on first iteration
                if i == 0:
                    writer.writerow(data.keys())

                for value in values:
                    row.append(value['value'])
            writer.writerow(row)
        return buff

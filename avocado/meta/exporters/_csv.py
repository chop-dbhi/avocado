import csv
from avocado.meta.exporters._base import BaseExporter

class CSVExporter(BaseExporter):
    preferred_formats = ('number', 'string')

    def write(self, buff):
        """Export to csv method
        `buff` - file-like object that is being written to
        """
        writer = csv.writer(buff, quoting=csv.QUOTE_MINIMAL)

        header = []
        for i, row_gen in enumerate(self.read()):
            row = []
            for data in row_gen:
                if i == 0:
                    # Build up header row
                    header.extend(data.keys())
                # Add formatted section to the row
                row.extend(data.values())
            # Write headers on first iteration
            if i == 0:
                writer.writerow(header)
            writer.writerow(row)
        return buff

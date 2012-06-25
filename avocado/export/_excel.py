from django.core.exceptions import ImproperlyConfigured
from avocado.conf import OPTIONAL_DEPS
if not OPTIONAL_DEPS['openpyxl']:
    raise ImproperlyConfigured('openpyxl must be installed to use this exporter.')

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from _base import BaseExporter


class ExcelExporter(BaseExporter):
    file_extension = 'xlsx'
    preferred_formats = ('boolean', 'number', 'string')

    def write(self, iterable, buff=None):
        buff = self.get_file_obj(buff)

        # Create the workbook and sheets
        wb = Workbook(optimized_write=True)
        ws_data = wb.create_sheet()
        ws_data.title = 'Data'
        ws_dict = wb.create_sheet()
        ws_dict.title = 'Data Dictionary'

        # Create the Data Dictionary Worksheet
        ws_dict.append(('Field Name', 'Data Type', 'Description',
            'Concept Name', 'Concept Discription'))

        for c in self.concepts:
            cfields = c.concept_fields.select_related('field')
            for cfield in cfields:
                datafield = cfield.field
                ws_dict.append((datafield.field_name, datafield.simple_type,
                    datafield.description, c.name, c.description))

        header = []
        # Create the data worksheet
        for i, row_gen in enumerate(self.read(iterable)):
            row = []
            for data in row_gen:
                if i == 0:
                    # Build up header row
                    header.extend(data.keys())
                # Add formatted section to the row
                row.extend(data.values())
            # Write headers on first iteration
            if i == 0:
                ws_data.append(header)
            ws_data.append(row)

        # Save the workbook
        if isinstance(buff, file):
            wb.save(buff)
        else:
            buff.write(save_virtual_workbook(wb))
        return buff

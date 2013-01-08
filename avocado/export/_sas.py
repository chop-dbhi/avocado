from zipfile import ZipFile
from cStringIO import StringIO
from string import punctuation
from django.template import Context
from django.template.loader import get_template
from _base import BaseExporter
from _csv import CSVExporter


class SASExporter(BaseExporter):
    short_name = 'SAS'
    long_name = 'Statistical Analysis System (SAS)'

    file_extension = 'zip'
    content_type = 'application/zip'

    preferred_formats = ('sas', 'coded', 'number', 'string')

    num_lg_names = 0

    # informat/format mapping for all datatypes except strings
    sas_informat_map = {
        'key': 'best32.',
        'number': 'best32.',
        'date': 'MMDDYYw.',
        'boolean': 'best32.',
        'datetime': 'DATETIMEw.d',
        'time': 'TIMEw.d'
    }

    sas_format_map = {
        'key': 'best12.',
        'number': 'best12.',
        'date': 'MMDDYYw.',
        'boolean': 'best12.',
        'datatime': 'DATETIMEw.d',
        'time': 'TIMEw.d'
    }

    def _format_name(self, name):
        punc = punctuation.replace('_', '')
        name = str(name).translate(None, punc)
        name = name.replace(' ', '_')
        if name[0].isdigit():
            name = '_' + name
        if len(name) < 30:
            return name
        self.num_lg_names += 1
        sas_name = name[:20]
        sas_name += '_lg_{0}'.format(self.num_lg_names)
        return sas_name

    def _get_formats(self, sas_name, datafield):
        """This method creates the sas format and informat lists for
        every variable.
        """
        # get the informat/format
        if datafield.simple_type == 'string':
            informat = s_format = '${0}.'.format(datafield.field.max_length)
        else:
            s_format = self.sas_format_map[datafield.simple_type]
            informat = self.sas_informat_map[datafield.simple_type]

        sas_informat = '{0:<10}{1:>10}'.format(sas_name, informat)
        sas_format = '{0:<10}{1:>10}'.format(sas_name, s_format)
        return sas_format, sas_informat

    def _code_values(self, name, field):
        """If field can be coded return the value dictionary
        and the format name for the dictionary
        """
        value_format = '{0} {0}_f.'.format(name)
        value = '{0}_f'.format(name)

        codes = []
        for i, (code, label) in enumerate(field.coded_choices):
            codes.append('{0}="{1}"'.format(code, label))

        values = '{0} {1}'.format(value, '\t'.join(codes))
        return value_format, values

    def write(self, iterable, buff=None, template_name='export/script.sas', *args, **kwargs):
        zip_file = ZipFile(self.get_file_obj(buff), 'w')

        formats = []            # sas formats for all fields
        informats = []          # sas informats for all fields
        inputs = []             # field names in sas format
        values = []             # sas value dictionaries
        value_formats = []      # labels for value dictionary
        labels = []             # labels the field names

        for c in self.concepts:
            cfields = c.concept_fields.select_related('datafield')
            for cfield in cfields:
                field = cfield.field
                name = self._format_name(field.field_name)

                # Setting up formats/informats
                format, informat = self._get_formats(name, field)
                formats.append(format)
                informats.append(informat)

                # Add the field names to the input statement
                if field.simple_type == 'string':
                    inputs.append('{0} $'.format(name))
                else:
                    inputs.append(name)

                # If a field can be coded create a SAS PROC Format statement
                # that creates a value dictionary
                if field.lexicon:
                    value_format, value = self._code_values(name, field)
                    value_formats.append(value_format)
                    values.append(value)

                # construct labels
                labels.append('{0}="{1}"'.format(name, str(cfield)))

        data_filename = 'data.csv'
        script_filename = 'script.sas'

        # File buffers
        data_buff = StringIO()
        # Create the data file
        data_exporter = CSVExporter(self.concepts)
        # Overwrite preferred formats for data file
        data_exporter.preferred_formats = self.preferred_formats
        data_exporter.write(iterable, data_buff, *args, **kwargs)

        zip_file.writestr(data_filename, data_buff.getvalue())

        template = get_template(template_name)
        context = Context({
            'data_filename': data_filename,
            'informats': informats,
            'formats': formats,
            'inputs': inputs,
            'labels': labels,
            'values': values,
            'value_formats': value_formats,
        })

        # Write script from template
        zip_file.writestr(script_filename, template.render(context))
        zip_file.close()

        return zip_file

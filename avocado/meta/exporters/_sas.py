from zipfile import ZipFile
from cStringIO import StringIO
from string import punctuation

from avocado.meta.exporters._base import BaseExporter
from avocado.meta.exporters._csv import CSVExporter

class SasExporter(BaseExporter):
    preferred_formats = ('coded', 'number', 'string')

    num_lg_names = 0

    # informat/format mapping for all datatypes except strings
    sas_informat_map = {
        'number': 'best32.',
        'date': 'MMDDYYw.',
        'boolean': 'best32.',
        'datetime': 'DATETIMEw.d',
        'time': 'TIMEw.d'
    }

    sas_format_map = {
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
        else:
            self.num_lg_names += 1
            sas_name = name[:20]
            sas_name += '_lg_{0}'.format(self.num_lg_names)
            return sas_name

    def _get_formats(self, sas_name, field):
        """This method creates the sas format and informat lists for
        every variable.
        """
        # get the informat/format
        if field.datatype == 'string':
            informat = s_format = '${0}.'.format(field.field.max_length)
        else:
            s_format = self.sas_format_map[field.datatype]
            informat = self.sas_informat_map[field.datatype]
        sas_informat = '\tinformat {0:<10}{1:>10};\n'.format(
                sas_name, informat)
        sas_format = '\tformat {0:<10}{1:>10};\n'.format(
                sas_name, s_format)

        return sas_format, sas_informat

    def _code_value(self, name, field):
        """If field can be coded return the value dictionary
        and the format name for the dictionary
        """
        value_format = '\tformat {0} {0}_f.;\n'.format(name)
        value = '\tvalue {0}_f '.format(name)

        for i, (val, code) in enumerate(field.coded_values):
            value += '{0}="{1}" '.format(code, val)
            if (i != len(field.coded_values)-1 and (i % 2) == 1 and i != 0):
                value += '\n\t\t'
        value += ';\n'

        return value_format, value

    def write(self, buff):
        zip_file = ZipFile(buff, 'w')
        script = StringIO()

        script.write('data SAS_EXPORT;\n')
        script.write('INFILE "data.csv" TRUNCOVER DSD firstobs=2;\n')

        inputs = ''          # field names in sas format
        values = ''          # sas value dictionaries
        value_formats = ''   # labels for value dictionary
        labels = ''          # labels the field names
        informats = ''      # sas informats for all fields
        formats = ''        # sas formats for all fields

        for c in self.concepts:
            cfields = c.conceptfields.select_related('field')
            for cfield in cfields:
                field = cfield.field
                name = self._format_name(field.field_name)

                # setting up formats/informats
                sas_form = self._get_formats(name, field)
                formats += sas_form[0]
                informats += sas_form[1]

                # add the field names to the input statement
                inputs += '\t\t' + name
                if field.datatype == 'string':
                    inputs += ' $'
                inputs += '\n'

                # if a field can be coded create a SAS PROC Format statement
                # that creates a value dictionary
                if field.coded_values:
                   codes = self._code_value(name, field)
                   value_formats += codes[0]
                   values += codes[1]

                # construct labels
                labels += '\tlabel {0}="{1}";\n'.format(name, field.description)

        # Write the SAS File
        script.write(informats + '\n')
        script.write(formats + '\n')
        script.write('input\n' + inputs +';\n\nrun;\n')
        script.write('proc contents;run;\n\ndata SAS_EXPORT;\n')
        script.write('\tset SAS_EXPORT;\n')
        script.write(labels +'\trun;\n\n')
        script.write('proc format;\n')
        script.write(values + '\nrun;\n\n')
        script.write('data SAS_EXPORT;\n\tset SAS_EXPORT;\n\n')
        script.write(value_formats + 'run;\n\n')
        script.write('/*proc contents data=SAS_EXPORT;*/\n')
        script.write('/*proc print data=SAS_EXPORT;*/\n')
        script.write('run;\nquit;\n')

        zip_file.writestr('export.sas', script.getvalue())
        script.close()

        # Write data CSV
        csv_file = StringIO()
        csv_export = CSVExporter(self.queryset, self.concepts)
        csv_export.preferred_formats = self.preferred_formats
        zip_file.writestr('data.csv', csv_export.write(csv_file).getvalue())
        csv_file.close()

        zip_file.close()
        return zip_file

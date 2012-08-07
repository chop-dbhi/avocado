from zipfile import ZipFile
from cStringIO import StringIO
from string import punctuation
from _base import BaseExporter
from _csv import CSVExporter


class SasExporter(BaseExporter):
    file_extension = 'zip'
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

        sas_informat = '\tinformat {0:<10}{1:>10};\n'.format(sas_name, informat)
        sas_format = '\tformat {0:<10}{1:>10};\n'.format(sas_name, s_format)
        return sas_format, sas_informat

    def _code_values(self, name, field):
        """If field can be coded return the value dictionary
        and the format name for the dictionary
        """
        value_format = '\tformat {0} {0}_f.;\n'.format(name)
        value = '\tvalue {0}_f '.format(name)
        values_len = len(field.codes)

        for i, (val, code) in enumerate(field.codes):
            value += '{0}="{1}" '.format(code, val)
            if (i != values_len - 1 and (i % 2) == 1 and i != 0):
                value += '\n\t\t'
        value += ';\n'

        return value_format, value

    def write(self, iterable, buff=None):
        buff = self.get_file_obj(buff)

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
            cfields = c.concept_fields.select_related('datafield')
            for cfield in cfields:
                field = cfield.field
                name = self._format_name(field.field_name)

                # setting up formats/informats
                sas_form = self._get_formats(name, field)
                formats += sas_form[0]
                informats += sas_form[1]

                # add the field names to the input statement
                inputs += '\t\t' + name
                if field.simple_type == 'string':
                    inputs += ' $'
                inputs += '\n'

                # if a field can be coded create a SAS PROC Format statement
                # that creates a value dictionary
                if field.lexicon:
                    codes = self._code_values(name, field)
                    value_formats += codes[0]
                    values += codes[1]

                # construct labels
                labels += '\tlabel {0}="{1}";\n'.format(name, field.description)

        # Write the SAS File
        script.write(informats + '\n')
        script.write(formats + '\n')
        script.write('input\n' + inputs + ';\n\nrun;\n')
        script.write('proc contents;run;\n\ndata SAS_EXPORT;\n')
        script.write('\tset SAS_EXPORT;\n')
        script.write(labels + '\trun;\n\n')
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
        csv_export = CSVExporter(self.concepts)
        csv_export.preferred_formats = self.preferred_formats
        zip_file.writestr('data.csv', csv_export.write(iterable, csv_file).getvalue())
        csv_file.close()

        zip_file.close()
        return zip_file

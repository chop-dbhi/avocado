from zipfile import ZipFile
from cStringIO import StringIO
from string import punctuation
from _base import BaseExporter
from _csv import CSVExporter


class RExporter(BaseExporter):
    file_extension = 'zip'
    preferred_formats = ('coded', 'number', 'string')

    def _format_name(self, name):
        punc = punctuation.replace('_', '')
        name = str(name).translate(None, punc)
        name = name.replace(' ', '_')
        words = name.split('_')
        for i, w in enumerate(words):
            if i == 0:
                name = w.lower()
                continue
            name += w.capitalize()
        if name[0].isdigit():
            name = '_' + name

        return name

    def _code_values(self, name, field):
        "If the field can be coded return the r factor and level for it."
        data_field = 'data${0}'.format(name)

        factor = '{0}.factor = factor({0},levels=c('.format(data_field)
        level = 'levels({0}.factor)=c('.format(data_field)

        values_len = len(field.codes)

        for i, (val, code) in enumerate(field.codes):
            factor += str(code)
            level += '"{0}"'.format(str(val))
            if i == values_len - 1:
                factor += '))\n'
                level += ')\n'
                continue
            factor += ' ,'
            level += ' ,'
        return factor, level

    def write(self, iterable, buff=None):
        buff = self.get_file_obj(buff)

        zip_file = ZipFile(buff, 'w')
        script = StringIO()

        script.write('# Read Data\ndata=read.csv("data.csv")\n\n')
        factors = []      # field names
        levels = []       # value dictionaries
        labels = []       # data labels

        for c in self.concepts:
            cfields = c.concept_fields.all()
            for cfield in cfields:
                field = cfield.field
                name = self._format_name(field.field_name)
                labels.append('attr(data${0}, "label") = "{1}"'.format(name, field.description))

                if field.lexicon:
                    codes = self._code_values(name, field)
                    factors.append(codes[0])
                    levels.append(codes[1])

        # Write out the r file to the given scripter
        script.write('# Setting Labels\n')
        script.write('\n'.join(labels) + '\n\n')

        script.write('# Setting Factors\n')
        script.write(''.join(factors) + '\n')

        script.write('# Setting Levels\n')
        script.write(''.join(levels) + '\n')

        zip_file.writestr('export.R', script.getvalue())
        script.close()

        # WRITE CSV
        csv_file = StringIO()
        csv_export = CSVExporter(self.concepts)
        csv_export.preferred_formats = self.preferred_formats
        zip_file.writestr('data.csv', csv_export.write(iterable, csv_file).getvalue())
        csv_file.close()

        zip_file.close()
        return zip_file

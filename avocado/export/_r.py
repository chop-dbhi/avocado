from zipfile import ZipFile
from cStringIO import StringIO
from string import punctuation
from django.template import Context
from django.template.loader import get_template
from _base import BaseExporter
from _csv import CSVExporter


class RExporter(BaseExporter):
    short_name = 'R'
    long_name = 'R Programming Language'

    file_extension = 'zip'
    content_type = 'application/zip'

    preferred_formats = ('r', 'coded')

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

    def _code_values(self, var, coded_labels):
        "If the field can be coded return the r factor and level for it."
        data_field = u'data${0}'.format(var)

        factor = u'{0}.factor = factor({0},levels=c('.format(data_field)
        level = u'levels({0}.factor)=c('.format(data_field)

        last = len(coded_labels) - 1

        for i, (code, label) in enumerate(coded_labels):
            factor += str(code)
            level += u'"{0}"'.format(str(label))

            # Do not apply on the final loop
            if i < last:
                factor += ' ,'
                level += ' ,'

        factor += '))\n'
        level += ')\n'

        return factor, level

    def write(self, iterable, buff=None, template_name='export/script.R',
              *args, **kwargs):

        zip_file = ZipFile(self.get_file_obj(buff), 'w')

        factors = []      # field names
        levels = []       # value dictionaries
        labels = []       # data labels

        for f in self.header:
            name = f['name']

            labels.append(u'attr(data${0}, "label") = "{1}"'
                          .format(name, f['label']))

            coded_labels = f['field'].coded_labels()

            if coded_labels:
                codes = self._code_values(name, f['field'], coded_labels)
                factors.append(codes[0])
                levels.append(codes[1])

        data_filename = 'data.csv'
        script_filename = 'script.R'

        # File buffers
        data_buff = StringIO()

        # Create the data file with this exporter's preferred formats.
        data_exporter = CSVExporter(self.concepts,
                                    preferred_formats=self.preferred_formats)

        # Write the data file.
        data_exporter.write(iterable, data_buff, *args, **kwargs)

        zip_file.writestr(data_filename, data_buff.getvalue())

        template = get_template(template_name)
        context = Context({
            'data_filename': data_filename,
            'labels': labels,
            'factors': factors,
            'levels': levels,
        })

        # Write script from template
        zip_file.writestr(script_filename, template.render(context))
        zip_file.close()

        return zip_file

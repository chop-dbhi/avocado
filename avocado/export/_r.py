from zipfile import ZipFile
from string import punctuation
from django.template import Context
from django.template.loader import get_template
from _base import Exporter, get_file_obj
from _csv import CSVExporter


class RExporter(Exporter):
    short_name = 'R'
    long_name = 'R Programming Language'

    file_extension = 'zip'
    content_type = 'application/zip'

    preferred_formats = ('r', 'coded', 'number', 'string')

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
        data_field = u'data${0}'.format(name)

        factor = u'{0}.factor = factor({0},levels=c('.format(data_field)
        level = u'levels({0}.factor)=c('.format(data_field)

        values_len = len(field.codes)

        for i, (code, label) in enumerate(field.coded_choices()):
            factor += str(code)
            level += u'"{0}"'.format(str(label))
            if i == values_len - 1:
                factor += '))\n'
                level += ')\n'
                continue
            factor += ' ,'
            level += ' ,'
        return factor, level

    def write_data(self, *args, **kwargs):
        """Creates the in-memory buffer of CSV data using this exporter's
        `preferred_formats`.
        """
        exporter = CSVExporter(self.iterator, self.concepts,
            preferred_formats=self.preferred_formats)
        return exporter.write(*args, **kwargs)

    def write_script(self, *args, **kwargs):
        "Write the script file for export."

        template_name = kwargs.get('template_name', 'export/script.R')
        data_filename = kwargs.get('data_filename', 'data.csv')

        factors = []      # field names
        levels = []       # value dictionaries
        labels = []       # data labels

        # TODO, these should use a cached version of the concepts if available
        # by the base exporter class.
        for c in self.concepts:
            cfields = c.concept_fields.all()
            for cfield in cfields:
                field = cfield.field
                name = self._format_name(field.field_name)
                labels.append(u'attr(data${0}, "label") = "{1}"'.format(name, unicode(cfield)))

                if field.supports_coded_values:
                    codes = self._code_values(name, field)
                    factors.append(codes[0])
                    levels.append(codes[1])

        template = get_template(template_name)
        context = Context({
            'data_filename': data_filename,
            'labels': labels,
            'factors': factors,
            'levels': levels,
        })

        return template.render(context)

    def write(self, buff=None, *args, **kwargs):
        """Creates a in-memory or file-based zipfile containing the script
        and data files.
        """
        kwargs.setdefault('data_filename', 'data.csv')
        kwargs.setdefault('script_filename', 'script.R')

        buff = get_file_obj(buff)
        zip_file = ZipFile(buff, 'w')

        # Write data
        data_buff = self.write_data(*args, **kwargs)
        zip_file.writestr(kwargs['data_filename'], data_buff.getvalue())

        # Write script
        script_str = self.write_script(*args, **kwargs)
        zip_file.writestr(kwargs['script_filename'], script_str)

        zip_file.close()
        return zip_file

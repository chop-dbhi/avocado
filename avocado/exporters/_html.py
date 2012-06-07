from django.template import Context
from django.template.loader import get_template
from _base import BaseExporter


class HTMLExporter(BaseExporter):
    preferred_formats = ('html', 'string')

    def write(self, iterable, buff=None, template=None):
        generator = self.read(iterable)

        if template:
            context = Context({'rows': generator})
            if isinstance(template, basestring):
                template = get_template(template)
            return template.render(context)

        buff = self.get_file_obj(buff)
        for row in generator:
            for item in row:
                buff.write(item)
        return buff

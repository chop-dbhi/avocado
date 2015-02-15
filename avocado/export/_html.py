from django.template import Context
from django.template.loader import get_template
from _base import BaseExporter


class HTMLExporter(BaseExporter):
    short_name = 'HTML'
    long_name = 'HyperText Markup Language (HTML)'

    file_extension = 'html'
    content_type = 'text/html'

    preferred_formats = ('html', 'string')

    def write(self, iterable, template, buff=None, *args, **kwargs):
        buff = self.get_file_obj(buff)

        if isinstance(template, basestring):
            template = get_template(template)

        context = Context({
            'header': self.header,
            'rows': iterable,
        })

        buff.write(template.render(context))

        return buff

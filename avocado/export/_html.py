from django.template import Context
from django.template.loader import get_template
from _base import Exporter, get_file_obj


class HTMLExporter(Exporter):
    short_name = 'HTML'
    long_name = 'HyperText Markup Language (HTML)'

    file_extension = 'html'
    content_type = 'text/html'

    preferred_formats = ('html', 'string')

    def write(self, template, buff=None, *args, **kwargs):
        buff = get_file_obj(buff)

        if isinstance(template, basestring):
            template = get_template(template)

        context = Context({'rows': iter(self)})
        buff.write(template.render(context))
        return buff

from django.template import Context
from django.template.loader import get_template
from _base import BaseExporter


class HTMLExporter(BaseExporter):
    preferred_formats = ('html', 'string')

    def write(self, iterable, buff=None, template=None):
        if not buff and not template:
            raise Exception('Either a file-like object or template must be supplied')

        generator = self.read(iterable)

        if buff:
            for row in generator:
                buff.write(row)
            return buff

        context = Context({'rows': generator})
        if isinstance(template, basestring):
            template = get_template(template)
        return template.render(context)

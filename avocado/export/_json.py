import inspect
from django.core.serializers.json import DjangoJSONEncoder
from _base import Exporter, get_file_obj


class JSONGeneratorEncoder(DjangoJSONEncoder):
    "Handle generator objects and expressions."
    def default(self, obj):
        if isinstance(obj, Exporter):
            return (row for row in obj)
        if inspect.isgenerator(obj):
            return list(obj)
        return self.default(obj)


class JSONExporter(Exporter):
    short_name = 'JSON'
    long_name = 'JavaScript Object Notation (JSON)'

    file_extension = 'json'
    content_type = 'application/json'

    preferred_formats = ('json', 'number', 'string')

    def write(self, buff=None, *args, **kwargs):
        buff = get_file_obj(buff)

        encoder = JSONGeneratorEncoder()
        for i, chunk in enumerate(encoder.iterencode(self)):
            buff.write(chunk)
        return buff

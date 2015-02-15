import inspect
from django.core.serializers.json import DjangoJSONEncoder
from _base import BaseExporter


class JSONGeneratorEncoder(DjangoJSONEncoder):
    "Handle generator objects and expressions."
    def default(self, obj):
        if inspect.isgenerator(obj):
            return list(obj)

        return super(JSONGeneratorEncoder, self).default(obj)


class JSONExporter(BaseExporter):
    short_name = 'JSON'
    long_name = 'JavaScript Object Notation (JSON)'

    file_extension = 'json'
    content_type = 'application/json'

    preferred_formats = ('json',)

    def write(self, iterable, buff=None, *args, **kwargs):
        buff = self.get_file_obj(buff)

        encoder = JSONGeneratorEncoder()

        keys = [f['name'] for f in self.header]

        data = [dict(zip(keys, values)) for values in iterable]

        for chunk in encoder.iterencode(data):
            buff.write(chunk)

        return buff

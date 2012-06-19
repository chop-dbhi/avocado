import json
import inspect
from _base import BaseExporter


class JSONGeneratorEncoder(json.JSONEncoder):
    "Handle generator objects and expressions."
    def default(self, obj):
        if inspect.isgenerator(obj):
            return list(obj)
        return super(JSONGeneratorEncoder, self).default(obj)


class JSONExporter(BaseExporter):
    file_extension = 'json'
    preferred_formats = ('number', 'string')

    def write(self, iterable, buff=None):
        buff = self.get_file_obj(buff)

        encoder = JSONGeneratorEncoder()
        for chunk in encoder.iterencode(self.read(iterable)):
            buff.write(chunk)
        return buff

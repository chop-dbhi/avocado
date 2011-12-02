import json
import inspect
from avocado.meta.exporters._base import BaseExporter

class JSONGeneratorEncoder(json.JSONEncoder):
    "Handle generator objects and expressions."
    def default(self, obj):
        if inspect.isgenerator(obj):
            return list(obj)
        return super(JSONGeneratorEncoder, self).default(obj)


class JSONExporter(BaseExporter):

    preferred_formats = ('number', 'string')

    def write(self, buff):
        """Export to csv method
        `buff` - file-like object that is being written to
        """
        encoder = JSONGeneratorEncoder()
        for chunk in encoder.iterencode(self.read()):
            buff.write(chunk)

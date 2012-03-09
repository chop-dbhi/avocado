from avocado.core import loader
from _csv import CSVExporter
from _sas import SasExporter
from _r import RExporter
from _json import JSONExporter
# This means the openpyxl library is not installed
try:
    from _excel import ExcelExporter
except ImportError:
    ExcelExporter = None

registry = loader.Registry(register_instance=False)

registry.register(CSVExporter)
registry.register(SasExporter)
registry.register(RExporter)
registry.register(JSONExporter)
if ExcelExporter:
    registry.register(ExcelExporter)

loader.autodiscover('exporters')

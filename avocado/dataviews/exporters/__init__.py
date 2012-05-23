from avocado.core import loader
from avocado.conf import INSTALLED_LIBS
from _csv import CSVExporter
from _sas import SasExporter
from _r import RExporter
from _json import JSONExporter

registry = loader.Registry(register_instance=False)

registry.register(CSVExporter)
registry.register(SasExporter)
registry.register(RExporter)
registry.register(JSONExporter)

if INSTALLED_LIBS['openpyxl']:
    from _excel import ExcelExporter
    registry.register(ExcelExporter)

loader.autodiscover('exporters')

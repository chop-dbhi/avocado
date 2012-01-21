from avocado.core import loader
from _csv import CSVExporter
from _excel import ExcelExporter
from _sas import SasExporter
from _r import RExporter
from _json import JSONExporter

registry = loader.Registry()

registry.register(CSVExporter)
registry.register(ExcelExporter)
registry.register(SasExporter)
registry.register(RExporter)
registry.register(JSONExporter)

loader.autodiscover('exporters')

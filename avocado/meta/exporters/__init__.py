from avocado.utils import loader
from avocado.meta.exporters._csv import CSVExporter
from avocado.meta.exporters._excel import ExcelExporter
from avocado.meta.exporters._sas import SasExporter
from avocado.meta.exporters._r import RExporter
from avocado.meta.exporters._json import JSONExporter

registry = loader.Registry()

registry.register(CSVExporter)
registry.register(ExcelExporter)
registry.register(SasExporter)
registry.register(RExporter)
registry.register(JSONExporter)

loader.autodiscover('exporters')

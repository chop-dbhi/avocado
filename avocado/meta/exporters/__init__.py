from avocado.utils import loader
from avocado.meta.exporters._csv import CSVExporter
from avocado.meta.exporters._excel import ExcelExporter
from avocado.meta.exporters._sas import SasExporter
from avocado.meta.exporters._r import RExporter

registry = loader.Registry()

registry.register(CSVExporter)
registry.register(ExcelExporter)
registry.register(SasExporter)
registry.register(RExporter)

loader.autodiscover('exporters')

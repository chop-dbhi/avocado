from avocado.core import loader
from avocado.conf import OPTIONAL_DEPS
from _base import BaseExporter  # noqa
from _csv import CSVExporter
from _sas import SASExporter
from _r import RExporter
from _json import JSONExporter
from _html import HTMLExporter  # noqa

registry = loader.Registry(register_instance=False)

registry.register(CSVExporter, CSVExporter.short_name.lower())
registry.register(SASExporter, SASExporter.short_name.lower())
registry.register(RExporter, RExporter.short_name.lower())
registry.register(JSONExporter, JSONExporter.short_name.lower())
# registry.register(HTMLExporter, HTMLExporter.short_name.lower())

if OPTIONAL_DEPS['openpyxl']:
    from _excel import ExcelExporter
    registry.register(ExcelExporter, ExcelExporter.short_name.lower())

loader.autodiscover('exporters')

from django.db import models
from avocado.models import ConceptInterface
from . import formatters

FORMATTER_CHOICES = formatters.registry.choices

class ExportInterface(ConceptInterface):
    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields
    formatter = models.CharField(max_length=100, blank=True, null=True,
        choices=FORMATTER_CHOICES)

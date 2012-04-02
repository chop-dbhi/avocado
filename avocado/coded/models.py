from django.db import models
from avocado.models import DataField

class CodedValue(models.Model):
    datafield = models.ForeignKey(DataField)
    value = models.CharField(max_length=100)
    coded = models.IntegerField()

    class Meta(object):
        app_label = 'avocado'
        unique_together = ('datafield', 'value')
        verbose_name = 'coded value'
        verbose_name_plural = 'coded values'
        ordering = ('value',)

    def natural_key(self):
        return self.datafield_id, self.value

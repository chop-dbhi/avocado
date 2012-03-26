from django.db import models
from avocado.models import Field

class CodedValue(models.Model):
    field = models.ForeignKey(Field)
    value = models.CharField(max_length=100)
    coded = models.IntegerField()

    class Meta(object):
        app_label = 'avocado'
        unique_together = ('field', 'value')
        verbose_name = 'coded value'
        verbose_name_plural = 'coded values'
        ordering = ('value',)

    def natural_key(self):
        return self.field_id, self.value




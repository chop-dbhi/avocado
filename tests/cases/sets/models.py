from django.db import models
from avocado.sets.models import ObjectSet, SetObject


class Record(models.Model):
    pass


class RecordSet(ObjectSet):
    set_object_rel = 'records'

    records = models.ManyToManyField(Record, through='RecordSetObject')


class RecordSetObject(SetObject):
    object_set = models.ForeignKey(RecordSet)
    set_object = models.ForeignKey(Record)

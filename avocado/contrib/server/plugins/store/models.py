from django.db import models
from avocado.store.models import ObjectSet

from production.models import Patient

__all__ = ('PatientSet',)

class PatientSet(ObjectSet):
    patients = models.ManyToManyField(Patient, editable=False)
    
    def bulk_insert(self, object_ids):
        field = self._meta.get_field_by_name('patients')[0]
        db_table = field.m2m_db_table()
        column_name = field.m2m_column_name()
        reverse_name = field.m2m_reverse_name()

        super(PatientSet, self).bulk_insert(object_ids, db_table,
            column_name, reverse_name)

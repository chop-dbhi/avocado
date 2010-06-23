from django.test import TestCase
from django import forms

from avocado.columns.models import ColumnConcept
from avocado.fields.models import FieldConcept

__all__ = ('FieldConceptTestCase',)

class FieldConceptTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def test_base(self):
        fc = FieldConcept.objects.get(pk=1)
        
        self.assertEqual(fc.model, ColumnConcept)
        self.assertEqual(fc.field, ColumnConcept._meta.get_field_by_name('name')[0])
        self.assertTrue(isinstance(fc.formfield(), forms.CharField))
    
    def test_formfield(self):
        fc = FieldConcept.objects.get(pk=3)
        
        self.assertTrue(isinstance(fc.formfield(), forms.CharField))
        

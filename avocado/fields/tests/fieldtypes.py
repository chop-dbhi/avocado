from django.test import TestCase
from django.core.exceptions import ValidationError

from avocado.fields.fieldtypes import *

__all__ = ('FieldTypeTestCase',)

class FieldTypeTestCase(TestCase):
    def test_integer(self):
        ft = IntegerField()
        
        self.assertEqual(ft.clean('exact', '5'), 5)
        self.assertEqual(ft.clean('gt', '5.3'), 5)
        
        self.assertEqual(ft.clean('in', '5'), 5)
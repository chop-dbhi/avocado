from django.test import TestCase
from django.core.exceptions import ValidationError

from avocado.fields.fieldtypes import *

__all__ = ('FieldTypeTestCase',)

class FieldTypeTestCase(TestCase):
    
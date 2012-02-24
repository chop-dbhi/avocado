from django.test import TestCase
from avocado.tests.base import BaseTestCase

__all__ = ('FieldTestCase', 'ConceptTestCase', 'DomainTestCase')

class FieldTestCase(BaseTestCase):

    def test_boolean(self):
        self.assertTrue(self.is_manager.model)
        self.assertTrue(self.is_manager.field)
        self.assertEqual(self.is_manager.datatype, 'boolean')
        self.assertEqual(self.is_manager.operators, ('exact', '-exact', 'isnull', '-isnull'))

    def test_integer(self):
        self.assertTrue(self.salary.model)
        self.assertTrue(self.salary.field)
        self.assertEqual(self.salary.datatype, 'number')
        self.assertEqual(self.salary.operators, ('exact', '-exact', 'in', '-in', 'lt', 'lte', 'gt', 'gte', 'range', 'isnull', '-isnull'))

    def test_string(self):
        self.assertTrue(self.first_name.model)
        self.assertTrue(self.first_name.field)
        self.assertEqual(self.first_name.datatype, 'string')
        self.assertEqual(self.first_name.operators, ('exact', '-exact', 'iexact', '-iexact', 'in', '-in', 'icontains', '-icontains'))


class ConceptTestCase(TestCase):
    pass


class DomainTestCase(TestCase):
    pass

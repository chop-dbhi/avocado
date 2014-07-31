from django.test import TestCase
from django.core import management
from avocado.models import DataField, DataConcept, DataConceptField
from avocado.query.validators import Validator, FieldValidator


class ValidatorTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

    def test_valid(self):
        v = Validator({})
        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, {})
        self.assertEqual(v.cleaned_data, {})


class FieldValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        super(FieldValidatorTestCase, self).setUp()
        self.field = DataField.objects.get_by_natural_key('tests.title.salary')
        self.concept = DataConcept(name='Salary', ident='salary')
        self.concept.save()
        DataConceptField(concept=self.concept, field=self.field).save()

    def test_valid_field_nk(self):
        "Field with natural key"
        data = {
            'field': 'tests.title.salary',
        }

        v = FieldValidator(data)

        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, data)
        self.assertEqual(v.cleaned_data['field'], self.field)

    def test_valid_field_nk_list(self):
        "Field with list-based natural key"
        data = {
            'field': ['tests', 'title', 'salary'],
        }

        v = FieldValidator(data)

        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, data)
        self.assertEqual(v.cleaned_data['field'], self.field)

    def test_valid_field_pk(self):
        "Field with primary key"
        data = {
            'field': self.field.pk,
        }

        v = FieldValidator(data)

        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, data)
        self.assertEqual(v.cleaned_data['field'], self.field)

    def test_valid_concept(self):
        "Field with concept primary key"
        data = {
            'field': self.field.pk,
            'concept': self.concept.pk,
        }

        v = FieldValidator(data)

        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, data)
        self.assertEqual(v.cleaned_data['field'], self.field)
        self.assertEqual(v.cleaned_data['concept'], self.concept)

    def test_valid_concept_ident(self):
        "Field with concept ident"
        data = {
            'field': self.field.pk,
            'concept': 'salary',
        }

        v = FieldValidator(data)

        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, data)
        self.assertEqual(v.cleaned_data['field'], self.field)
        self.assertEqual(v.cleaned_data['concept'], self.concept)

    def test_valid_concept_short_field(self):
        "Field short name with concept"
        data = {
            'field': 'salary',
            'concept': self.concept.pk,
        }

        v = FieldValidator(data)

        self.assertTrue(v.is_valid())
        self.assertEqual(v.data, data)
        self.assertEqual(v.cleaned_data['field'], self.field)
        self.assertEqual(v.cleaned_data['concept'], self.concept)

    def test_invalid_field(self):
        "Field does not exist"
        v = FieldValidator({
            'field': 'invalid.lookup',
        })

        self.assertFalse(v.is_valid())
        self.assertTrue('errors' in v.data)
        self.assertEqual(v.errors[0], 'field_does_not_exist')
        self.assertFalse(v.data['enabled'])

    def test_invalid_concept(self):
        "Concept does not exist"
        v = FieldValidator({
            'field': self.field.pk,
            'concept': 'does_not_exist',
        })

        self.assertFalse(v.is_valid())
        self.assertTrue('errors' in v.data)
        self.assertEqual(v.errors[0], 'concept_does_not_exist')
        self.assertFalse(v.data['enabled'])

    def test_invalid_field_for_concept(self):
        "Field not contained in concept"
        v = FieldValidator({
            'field': 'tests.title.name',
            'concept': self.concept.pk,
        })

        self.assertFalse(v.is_valid())
        self.assertTrue('errors' in v.data)
        self.assertEqual(v.errors[0], 'field_does_not_exist_for_concept')
        self.assertFalse(v.data['enabled'])

    def test_ambiguous_field(self):
        "Ambiguous field"
        # Could be the name for salary or project..
        v = FieldValidator({
            'field': 'name'
        })

        self.assertFalse(v.is_valid())
        self.assertTrue('errors' in v.data)
        self.assertEqual(v.errors[0], 'ambiguous_field')
        self.assertFalse(v.data['enabled'])

from django.core.exceptions import ValidationError
from avocado.tests.base import BaseTestCase
from avocado.query import parser

class ParserValidationTestCase(BaseTestCase):
    def test_valid(self):
        # Single by id
        self.assertEqual(parser.validate({
            'id': 4,
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Single by dotted label
        self.assertEqual(parser.validate({
            'id': 'tests.title.boss',
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Single by label list
        self.assertEqual(parser.validate({
            'id': ['tests', 'title', 'boss'],
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Branch node
        self.assertEqual(parser.validate({
            'type': 'and',
            'children': [{
                'id': 4,
                'operator': 'exact',
                'value': 'CEO',
            }, {
                'id': 5,
                'operator': 'exact',
                'value': 'John',
            }]
        }), None)

    def test_invalid(self):
        # Non-existent data field
        self.assertRaises(ValidationError, parser.validate, {
            'id': 99,
            'operator': 'exact',
            'value': 'CEO'
        })

        # Invalid structures
        # Object must be a dict
        self.assertRaises(ValidationError, parser.validate, [])

        # Object must be a dict
        self.assertRaises(ValidationError, parser.validate, None)

        # Invalid logical operator
        self.assertRaises(ValidationError, parser.validate, {'type': 'foo', 'children': []})

        # No children
        self.assertRaises(ValidationError, parser.validate, {'type': 'and', 'children': []})

        # 1 child
        self.assertRaises(ValidationError, parser.validate, {
            'type': 'and',
            'children': [{'id': 4, 'operator': 'exact', 'value': 'CEO'}]
        })

        # Missing 'value' key in first condition
        self.assertRaises(ValidationError, parser.validate, {
            'type': 'and',
            'children': [{
                'id': 4, 'operator': 'exact'
            }, {
                'id': 4, 'operator': 'exact', 'value': 'CEO'
            }]
        })

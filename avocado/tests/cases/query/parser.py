from django.core.exceptions import ValidationError
from avocado.tests.base import BaseTestCase
from avocado.query import parser

class ParserValidationTestCase(BaseTestCase):
    def test_valid(self):
        # Single by id
        self.assertEqual(parser.parse({'id': 4, 'operator': 'exact', 'value': 'CEO'}), None)
        # Single by dotted label
        self.assertEqual(parser.parse({'id': 'tests.title.boss', 'operator': 'exact', 'value': 'CEO'}), None)
        # Single by label list
        self.assertEqual(parser.parse({'id': ['tests', 'title', 'boss'], 'operator': 'exact', 'value': 'CEO'}), None)

        # Branch node
        self.assertEqual(parser.parse({
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
        self.assertRaises(ValidationError, parser.parse, {'id': 99, 'operator': 'exact', 'value': 'CEO'})

        # Invalid structures
        # Object must be a dict
        self.assertRaises(ValidationError, parser.parse, [])

        # Object must be a dict
        self.assertRaises(ValidationError, parser.parse, None)

        # Invalid logical operator
        self.assertRaises(ValidationError, parser.parse, {'type': 'foo', 'children': []})

        # No children
        self.assertRaises(ValidationError, parser.parse, {'type': 'and', 'children': []})

        # 1 child
        self.assertRaises(ValidationError, parser.parse, {
            'type': 'and',
            'children': [{'id': 4, 'operator': 'exact', 'value': 'CEO'}]
        })

        # Missing 'value' key in first condition
        self.assertRaises(ValidationError, parser.parse, {
            'type': 'and',
            'children': [{
                'id': 4, 'operator': 'exact'
            }, {
                'id': 4, 'operator': 'exact', 'value': 'CEO'
            }]
        })

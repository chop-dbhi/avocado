from django.core.exceptions import ValidationError
from avocado.tests.base import BaseTestCase
from avocado.query import parsers


class DataContextParserTestCase(BaseTestCase):
    def test_valid(self):
        # Single by id
        self.assertEqual(parsers.datacontext.validate({
            'id': 4,
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Single by dotted label
        self.assertEqual(parsers.datacontext.validate({
            'id': 'tests.title.boss',
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Single by label list
        self.assertEqual(parsers.datacontext.validate({
            'id': ['tests', 'title', 'boss'],
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Branch node
        self.assertEqual(parsers.datacontext.validate({
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
        self.assertRaises(ValidationError, parsers.datacontext.validate, {
            'id': 99,
            'operator': 'exact',
            'value': 'CEO'
        })

        # Invalid structures
        # Object must be a dict
        self.assertRaises(ValidationError, parsers.datacontext.validate, [])

        # Object must be a dict
        self.assertRaises(ValidationError, parsers.datacontext.validate, None)

        # Invalid logical operator
        self.assertRaises(ValidationError, parsers.datacontext.validate, {'type': 'foo', 'children': []})

        # No children
        self.assertRaises(ValidationError, parsers.datacontext.validate, {'type': 'and', 'children': []})

        # 1 child
        self.assertRaises(ValidationError, parsers.datacontext.validate, {
            'type': 'and',
            'children': [{'id': 4, 'operator': 'exact', 'value': 'CEO'}]
        })

        # Missing 'value' key in first condition
        self.assertRaises(ValidationError, parsers.datacontext.validate, {
            'type': 'and',
            'children': [{
                'id': 4, 'operator': 'exact'
            }, {
                'id': 4, 'operator': 'exact', 'value': 'CEO'
            }]
        })

    def test_apply(self):
        node = parsers.datacontext.parse({
            'id': 4,
            'operator': 'exact',
            'value': True
        })

        self.assertEqual(str(node.apply().values('id').query), 'SELECT "tests_employee"."id" FROM "tests_employee" INNER JOIN "tests_title" ON ("tests_employee"."title_id" = "tests_title"."id") WHERE ("tests_title"."boss" = True  AND "tests_employee"."title_id" IS NOT NULL)')
        self.assertEqual(node.language, {'operator': 'exact', 'language': u'Boss is True', 'id': 4, 'value': True})

        # Branch node
        node = parsers.datacontext.parse({
            'type': 'and',
            'children': [{
                'id': 4,
                'operator': 'exact',
                'value': True,
            }, {
                'id': 5,
                'operator': 'exact',
                'value': 'John',
            }]
        })

        self.assertEqual(str(node.apply().values('id').query), 'SELECT "tests_employee"."id" FROM "tests_employee" INNER JOIN "tests_title" ON ("tests_employee"."title_id" = "tests_title"."id") WHERE ("tests_employee"."first_name" = John  AND "tests_title"."boss" = True  AND "tests_employee"."title_id" IS NOT NULL)')
        self.assertEqual(node.language, {
            'type': 'and',
            'children': [{
                'id': 4,
                'operator': 'exact',
                'value': True,
                'language': 'Boss is True',
            }, {
                'id': 5,
                'operator': 'exact',
                'value': 'John',
                'language': 'First Name is equal to John',
            }]
        })


class DataViewParserTestCase(BaseTestCase):
    def test_valid(self):
        # Single by id
        self.assertEqual(parsers.datacontext.validate({
            'id': 4,
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Single by dotted label
        self.assertEqual(parsers.datacontext.validate({
            'id': 'tests.title.boss',
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Single by label list
        self.assertEqual(parsers.datacontext.validate({
            'id': ['tests', 'title', 'boss'],
            'operator': 'exact',
            'value': 'CEO'
        }), None)

        # Branch node
        self.assertEqual(parsers.datacontext.validate({
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
        self.assertRaises(ValidationError, parsers.datacontext.validate, {
            'id': 99,
            'operator': 'exact',
            'value': 'CEO'
        })

        # Invalid structures
        # Object must be a dict
        self.assertRaises(ValidationError, parsers.datacontext.validate, [])

        # Object must be a dict
        self.assertRaises(ValidationError, parsers.datacontext.validate, None)

        # Invalid logical operator
        self.assertRaises(ValidationError, parsers.datacontext.validate, {'type': 'foo', 'children': []})

        # No children
        self.assertRaises(ValidationError, parsers.datacontext.validate, {'type': 'and', 'children': []})

        # 1 child
        self.assertRaises(ValidationError, parsers.datacontext.validate, {
            'type': 'and',
            'children': [{'id': 4, 'operator': 'exact', 'value': 'CEO'}]
        })

        # Missing 'value' key in first condition
        self.assertRaises(ValidationError, parsers.datacontext.validate, {
            'type': 'and',
            'children': [{
                'id': 4, 'operator': 'exact'
            }, {
                'id': 4, 'operator': 'exact', 'value': 'CEO'
            }]
        })

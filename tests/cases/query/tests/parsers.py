from copy import deepcopy
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core import management
from avocado.query import parsers
from avocado.models import DataConcept, DataField, DataConceptField
from ..models import Employee


class DataContextParserTestCase(TestCase):
    fixtures = ['query.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'query', quiet=True)

    def test_valid(self):
        title = DataField.objects.get_by_natural_key('query.title.name')

        # Single by id (deprecated)
        attrs = {
            'id': title.pk,
            'operator': 'exact',
            'value': 'CEO',
            'language': 'Name is CEO'
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # Single by dotted label
        attrs = {
            'field': 'query.title.name',
            'operator': 'exact',
            'value': 'CEO',
            'language': 'Name is CEO'
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # Single by label list
        attrs = {
            'field': ['query', 'title', 'name'],
            'operator': 'exact',
            'value': 'CEO',
            'language': 'Name is CEO'
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # Single by field
        attrs = {
            'field': title.pk,
            'operator': 'exact',
            'value': 'CEO',
            'language': 'Name is CEO'
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # Branch node
        attrs = {
            'type': 'and',
            'children': [{
                'field': 'query.title.name',
                'operator': 'exact',
                'value': 'CEO',
                'language': 'Name is CEO'
            }, {
                'field': 'query.employee.first_name',
                'operator': 'exact',
                'value': 'John',
                'language': 'First Name is John'
            }],
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # No children
        attrs = {
            'type': 'and',
            'children': [],
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # 1 child
        attrs = {
            'type': 'and',
            'children': [{
                'field': 'query.title.name',
                'operator': 'exact',
                'value': 'CEO',
                'language': 'Name is CEO'
            }]
        }
        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

    def test_invalid(self):
        # Non-existent data field
        attrs = parsers.datacontext.validate({
            'field': 999,
            'operator': 'exact',
            'value': 'CEO'
        })
        self.assertFalse(attrs['enabled'])

        # Object must be a dict
        self.assertRaises(ValidationError, parsers.datacontext.validate, None)

        # Invalid logical operator
        attrs = parsers.datacontext.validate({'type': 'foo', 'children': []})
        self.assertFalse(attrs['enabled'])

        # Missing 'value' key in first condition
        attrs = parsers.datacontext.validate({
            'type': 'and',
            'children': [{
                'field': 'query.title.name',
                'operator': 'exact'
            }, {
                'field': 'query.title.name',
                'operator': 'exact',
                'value': 'CEO'
            }]
        }, tree=Employee)

        self.assertTrue(attrs.get('enabled', True))
        self.assertFalse(attrs['children'][0]['enabled'])
        self.assertTrue(attrs['children'][1].get('enabled', True))

    def test_field_for_concept(self):
        f = DataField.objects.get(model_name='title', field_name='name')
        c1 = DataConcept()
        c2 = DataConcept()
        c1.save()
        c2.save()
        cf = DataConceptField(concept=c1, field=f)
        cf.save()


        attrs = {
            'concept': c1.pk,
            'field': f.pk,
            'operator': 'exact',
            'value': 'CEO',
            'language': 'Name is CEO'
        }

        self.assertEqual(parsers.datacontext.validate(deepcopy(attrs), tree=Employee), attrs)

        # Invalid concept
        attrs = parsers.datacontext.validate({
            'concept': c2.pk,
            'field': f.pk,
            'operator': 'exact',
            'value': 'CEO',
        }, tree=Employee)

        self.assertFalse(attrs['enabled'])

    def test_parsed_node(self):
        node = parsers.datacontext.parse({
            'type': 'and',
            'children': [],
        }, tree=Employee)

        # No condition has been defined..
        self.assertEqual(node.condition, None)

        node = parsers.datacontext.parse({
            'type': 'and',
            'children': [{
                'field': 'query.title.name',
                'operator': 'exact',
                'value': 'CEO',
            }]
        }, tree=Employee)

        # Only the one condition is represented
        self.assertEqual(str(node.condition), "(AND: ('title__name__exact', u'CEO'))")

    def test_apply(self):
        node = parsers.datacontext.parse({
            'field': 'query.title.boss',
            'operator': 'exact',
            'value': True
        }, tree=Employee)

        self.assertEqual(unicode(node.apply().values('id').query), 'SELECT DISTINCT "query_employee"."id" FROM "query_employee" INNER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") WHERE "query_title"."boss" = True ')
        self.assertEqual(node.language, {'operator': 'exact', 'language': u'Boss is True', 'field': 4, 'value': True})

        # Branch node
        node = parsers.datacontext.parse({
            'type': 'and',
            'children': [{
                'field': 'query.title.boss',
                'operator': 'exact',
                'value': True,
            }, {
                'field': 'query.employee.first_name',
                'operator': 'exact',
                'value': 'John',
            }]
        }, tree=Employee)

        self.assertEqual(unicode(node.apply().values('id').query), 'SELECT DISTINCT "query_employee"."id" FROM "query_employee" INNER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") WHERE ("query_employee"."first_name" = John  AND "query_title"."boss" = True )')

        self.assertEqual(node.language, {
            'type': 'and',
            'children': [{
                'field': 4,
                'operator': 'exact',
                'value': True,
                'language': 'Boss is True',
            }, {
                'field': 5,
                'operator': 'exact',
                'value': 'John',
                'language': 'First Name is John',
            }]
        })

class DataViewParserTestCase(TestCase):
    fixtures = ['query.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'query', quiet=True)
        f1 = DataField.objects.get(pk=1)
        f2 = DataField.objects.get(pk=2)

        c1 = DataConcept()
        c1.save()

        DataConceptField(concept=c1, field=f1).save()
        DataConceptField(concept=c1, field=f2).save()

    def test_valid(self):
        # Single by id
        self.assertEqual(parsers.dataview.validate({
            'columns': [1],
        }, tree=Employee), None)

        self.assertEqual(parsers.dataview.validate({
            'ordering': [(1, 'desc')],
        }, tree=Employee), None)
    
    def test_apply(self):
        node = parsers.dataview.parse({
            'columns': [1],
        }, tree=Employee)
        self.assertEqual(unicode(node.apply().query), 'SELECT "query_employee"."id", "query_office"."location", "query_title"."name" FROM "query_employee" INNER JOIN "query_office" ON ("query_employee"."office_id" = "query_office"."id") LEFT OUTER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id")')

        node = parsers.dataview.parse({
            'ordering': [(1, 'desc')],
        }, tree=Employee)
        self.assertEqual(unicode(node.apply().query), 'SELECT "query_employee"."id" FROM "query_employee" INNER JOIN "query_office" ON ("query_employee"."office_id" = "query_office"."id") LEFT OUTER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") ORDER BY "query_office"."location" DESC, "query_title"."name" DESC')

    def test_apply_distinct(self):
        node = parsers.dataview.parse({
            'columns': [1],
        }, tree=Employee)
        self.assertEqual(unicode(node.apply(Employee.objects.distinct()).query), 'SELECT DISTINCT "query_employee"."id", "query_office"."location", "query_title"."name" FROM "query_employee" INNER JOIN "query_office" ON ("query_employee"."office_id" = "query_office"."id") LEFT OUTER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id")')

        node = parsers.dataview.parse({
            'ordering': [(1, 'desc')],
        }, tree=Employee)
        self.assertEqual(unicode(node.apply(Employee.objects.distinct()).query), 'SELECT DISTINCT "query_employee"."id", "query_office"."location", "query_title"."name" FROM "query_employee" INNER JOIN "query_office" ON ("query_employee"."office_id" = "query_office"."id") LEFT OUTER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") ORDER BY "query_office"."location" DESC, "query_title"."name" DESC')

class DataQueryParserTestCase(TestCase):
    fixtures = ['query.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'query', quiet=True)
        f1 = DataField.objects.get(pk=1)
        f2 = DataField.objects.get(pk=2)

        c1 = DataConcept()
        c1.save()

        DataConceptField(concept=c1, field=f1).save()
        DataConceptField(concept=c1, field=f2).save()

    def test_valid(self):
        self.assertEqual(parsers.dataquery.validate({}, tree=Employee), None)

        attrs = {
            'context': {
                'field': 'query.title.name',
                'operator': 'exact',
                'value': 'CEO',
                'language': 'Name is CEO'
            },
            'view': {
                'columns': [1],
            }
        }

        exp_attrs = deepcopy(attrs)
        exp_attrs['view'] = None
        
        self.assertEqual(
                parsers.dataquery.validate(deepcopy(attrs), tree=Employee), 
                exp_attrs)

        # Only the context
        attrs = {
            'context': {
                'field': 'query.title.name',
                'operator': 'exact',
                'value': 'CEO',
                'language': 'Name is CEO'
            }
        }
        self.assertEqual(
                parsers.dataquery.validate(deepcopy(attrs), tree=Employee), 
                attrs)
        
        # Only the view
        attrs = {
            'view': {
                'ordering': [(1, 'desc')],
            }
        }
        exp_attrs = {
            'view': None
        }
        self.assertEqual(
                parsers.dataquery.validate(attrs, tree=Employee), 
                exp_attrs)

    def test_parsed_node(self):
        # Make sure no context or view subnodes are created
        node = parsers.dataquery.parse({}, tree=Employee)
        self.assertEqual(node.datacontext_node, None)
        self.assertEqual(node.dataview_node, None)

        node = parsers.dataquery.parse({
            'context': {
                'type': 'and',
                'children': [],
            }
        }, tree=Employee)

        # No condition has been defined..
        self.assertEqual(node.datacontext_node.condition, None)

        node = parsers.dataquery.parse({
            'context': {
                'type': 'and',
                'children': [{
                    'field': 'query.title.name',
                    'operator': 'exact',
                    'value': 'CEO',
                }]
            }
        }, tree=Employee)

        # Only the one condition is represented
        self.assertEqual(
                str(node.datacontext_node.condition), 
                "(AND: ('title__name__exact', u'CEO'))")
    
    def test_apply(self):
        node = parsers.dataquery.parse({
            'context': {
                'field': 'query.title.boss',
                'operator': 'exact',
                'value': True
            },
            'view': {
                'columns': [1],
            }
        }, tree=Employee)
        
        self.assertEqual(unicode(node.apply().query), 'SELECT DISTINCT "query_employee"."id", "query_office"."location", "query_title"."name" FROM "query_employee" INNER JOIN "query_office" ON ("query_employee"."office_id" = "query_office"."id") LEFT OUTER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") WHERE "query_title"."boss" = True ')

        # Just the view
        node = parsers.dataquery.parse({
            'view': {
                'ordering': [(1, 'desc')],
            }
        }, tree=Employee)
        self.assertEqual(unicode(node.apply().query), 'SELECT "query_employee"."id" FROM "query_employee" INNER JOIN "query_office" ON ("query_employee"."office_id" = "query_office"."id") LEFT OUTER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") ORDER BY "query_office"."location" DESC, "query_title"."name" DESC')

        # Just the context
        node = parsers.dataquery.parse({
            'context': {
                'field': 'query.title.boss',
                'operator': 'exact',
                'value': True
            }
        }, tree=Employee)

        self.assertEqual(unicode(node.apply().values('id').query), 'SELECT DISTINCT "query_employee"."id" FROM "query_employee" INNER JOIN "query_title" ON ("query_employee"."title_id" = "query_title"."id") WHERE "query_title"."boss" = True ')
        self.assertEqual(node.datacontext_node.language, {'operator': 'exact', 'language': u'Boss is True', 'field': 4, 'value': True})

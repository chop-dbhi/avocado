try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.test import TestCase
from django.core import management
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from guardian.shortcuts import assign
from avocado.models import (DataField, DataConcept, DataConceptField,
    DataContext, DataView, DataQuery)


class ModelInstanceCacheTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'models', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('models', 'employee', 'is_manager')

    def test_datafield_cache(self):
        cache.clear()

        pk = self.is_manager.pk
        # New query, object is fetched from cache
        queryset = DataField.objects.filter(pk=pk)
        self.assertEqual(queryset._result_cache, None)

        self.is_manager.save()

        queryset = DataField.objects.filter(pk=pk)
        # Without this len test, the _result_cache will not be populated due to
        # the inherent laziness of the filter method.
        self.assertGreater(len(queryset), 0)
        self.assertEqual(queryset._result_cache[0].pk, pk)


class DataFieldTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'models', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('models', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('models', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key('models', 'employee', 'first_name')

    def test_boolean(self):
        self.assertTrue(self.is_manager.model)
        self.assertTrue(self.is_manager.field)
        self.assertEqual(self.is_manager.simple_type, 'boolean')
        self.assertEqual(self.is_manager.nullable, True)

    def test_integer(self):
        self.assertTrue(self.salary.model)
        self.assertTrue(self.salary.field)
        self.assertEqual(self.salary.simple_type, 'number')
        self.assertEqual(self.salary.nullable, True)

    def test_string(self):
        self.assertTrue(self.first_name.model)
        self.assertTrue(self.first_name.field)
        self.assertEqual(self.first_name.simple_type, 'string')
        self.assertEqual(self.first_name.nullable, False)


class DataFieldManagerTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'models', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('models', 'employee', 'is_manager')

    def test_published(self):
        # Published, not specific to any user
        self.assertEqual([x.pk for x in DataField.objects.published()], [])

        self.is_manager.published = True
        self.is_manager.save()

        # Now published, it will appear
        self.assertEqual([x.pk for x in DataField.objects.published()], [7])

        user1 = User.objects.create_user('user1', 'user1')
        user2 = User.objects.create_user('user2', 'user2')
        assign('avocado.view_datafield', user1, self.is_manager)

        # Now restrict the fields that are published and are assigned to users
        self.assertEqual([x.pk for x in DataField.objects.published(user1)], [7])
        # `user2` is not assigned
        self.assertEqual([x.pk for x in DataField.objects.published(user2)], [])


class DataConceptTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'models', quiet=True)

    def test_search(self):
        management.call_command('rebuild_index', interactive=False)

    def test_format(self):
        name_field = DataField.objects.get_by_natural_key('models', 'title', 'name')
        salary_field = DataField.objects.get_by_natural_key('models', 'title', 'salary')
        boss_field = DataField.objects.get_by_natural_key('models', 'title', 'boss')

        concept = DataConcept(name='Title')
        concept.save()

        DataConceptField(concept=concept, field=name_field, order=1).save()
        DataConceptField(concept=concept, field=salary_field, order=2).save()
        DataConceptField(concept=concept, field=boss_field, order=3).save()

        values = ['CEO', 100000, True]

        self.assertEqual(concept.format(values),
            OrderedDict([
                (u'name', u'CEO'),
                (u'salary', 100000),
                (u'boss', True)
            ]))

        self.assertEqual(concept._formatter_cache[0], None)

        from avocado.formatters import Formatter, registry as formatters

        class HtmlFormatter(Formatter):
            def to_html(self, values, **context):
                fvalues = self(values, preferred_formats=['string'])
                return OrderedDict({
                    'profile': '<span>' + '</span><span>'.join(fvalues.values()) + '</span>'
                })
            to_html.process_multiple = True

        formatters.register(HtmlFormatter, 'HTML')
        concept.formatter_name = 'HTML'

        self.assertEqual(concept.format(values, preferred_formats=['html']),
            OrderedDict([
                ('profile', u'<span>CEO</span><span>100000</span><span>True</span>')
            ]))


class DataConceptManagerTestCase(TestCase):
    fixtures = ['models.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'models', quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key('models', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('models', 'title', 'salary')

    def test_published(self):
        concept = DataConcept(published=True)
        concept.save()
        DataConceptField(concept=concept, field=self.is_manager).save()
        DataConceptField(concept=concept, field=self.salary).save()

        # Published, not specific to any user
        self.assertEqual([x.pk for x in DataConcept.objects.published()], [])

        self.is_manager.published = True
        self.is_manager.save()
        self.salary.published = True
        self.salary.save()

        # Now published, it will appear
        self.assertEqual([x.pk for x in DataConcept.objects.published()], [1])

        user1 = User.objects.create_user('user1', 'user1')

        # Nothing since user1 cannot view either datafield
        self.assertEqual([x.pk for x in DataConcept.objects.published(user1)], [])

        assign('avocado.view_datafield', user1, self.is_manager)
        # Still nothing since user1 has no permission for salary
        self.assertEqual([x.pk for x in DataConcept.objects.published(user1)], [])

        assign('avocado.view_datafield', user1, self.salary)
        # Now user1 can see the concept
        self.assertEqual([x.pk for x in DataConcept.objects.published(user1)], [1])

        user2 = User.objects.create_user('user2', 'user2')

        # `user2` is not assigned
        self.assertEqual([x.pk for x in DataConcept.objects.published(user2)], [])


class DataContextTestCase(TestCase):
    def test_init(self):
        json = {'field': 'models.title.salary', 'operator': 'gt', 'value': '1000'}
        cxt = DataContext(json)
        self.assertEqual(cxt.json, json)

    def test_clean(self):
        # Save a default template
        cxt = DataContext(template=True, default=True)
        cxt.save()

        # Save new template (not default)
        cxt2 = DataContext(template=True)
        cxt2.save()

        # Try changing it to default
        cxt2.default = True
        self.assertRaises(ValidationError, cxt2.save)

        cxt.save()


class DataViewTestCase(TestCase):
    def test_init(self):
        json = {'columns': []}
        view = DataView(json)
        self.assertEqual(view.json, json)

    def test_clean(self):
        # Save a default template
        view = DataView(template=True, default=True)
        view.save()

        # Save new template (not default)
        view2 = DataView(template=True)
        view2.save()

        # Try changing it to default
        view2.default = True
        self.assertRaises(ValidationError, view2.save)

        view.save()

class DataQueryTestCase(TestCase):
    def test_init(self):
        json = {
            'context': {'field': 'models.title.salary', 'operator': 'gt', 'value': '1000'},
            'view': {'columns': []}
        }

        query = DataQuery(json)
        self.assertEqual(query.context_json, json['context'])
        self.assertEqual(query.view_json, json['view'])

        # Test the json of the DataQuery properties too
        self.assertEqual(query.context.json, json['context'])
        self.assertEqual(query.view.json, json['view'])

    def test_clean(self):
        # Save default template
        query = DataQuery(template=True, default=True)
        query.save()

        # Save new template (not default)
        query2 = DataQuery(template=True)
        query2.save()

        # Try changing the second query to the default
        query2.default = True
        self.assertRaises(ValidationError, query2.save)

        query.save()

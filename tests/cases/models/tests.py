from copy import deepcopy
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.test import TestCase
from django.core import management
from django.test.utils import override_settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from guardian.shortcuts import assign
from avocado.models import DataField, DataConcept, DataConceptField, \
    DataContext, DataView, DataQuery, DataCategory
from ...models import Employee


class ModelInstanceCacheTestCase(TestCase):
    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')

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
    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'first_name')

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


class DataFieldMethodsTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)
        self.budget = DataField.objects.get_by_natural_key(
            'tests', 'project', 'budget')
        self.due_date = DataField.objects.get_by_natural_key(
            'tests', 'project', 'due_date')

    def test_sparsity(self):
        self.assertEqual(self.budget.sparsity(), 0.5)
        self.assertEqual(self.due_date.sparsity(), 1)


class DataFieldSupplementaryTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        self.f = DataField.init('tests.title.name')

    def test_default(self):
        self.assertEqual(list(self.f.values())[0], 'Analyst')
        self.assertEqual(list(self.f.labels())[0], 'Analyst')
        self.assertEqual(self.f.codes(), None)

        self.assertEqual(list(self.f.value_labels())[0],
                         ('Analyst', 'Analyst'))
        self.assertEqual(self.f.coded_values(), None)
        self.assertEqual(self.f.coded_labels(), None)

    def test_code_field(self):
        self.f.code_field_name = 'id'

        self.assertEqual(list(self.f.codes())[0], 2)
        self.assertEqual(list(self.f.coded_values())[0], (2, 'Analyst'))
        self.assertEqual(list(self.f.coded_labels())[0], (2, 'Analyst'))

    def test_predefined_choices(self):
        choices = (
            ('Programmer', 'Programmer'),
            ('Analyst', 'Analyst'),
            ('QA', 'QA'),
            ('CEO', 'CEO'),
            ('IT', 'IT'),
            ('Guard', 'Guard'),
            ('Lawyer', 'Lawyer'),
        )

        # Manually set choices for test..
        self.f.field._choices = choices

        self.assertEqual(list(self.f.values())[0], 'Programmer')
        self.assertEqual(list(self.f.labels())[0], 'Programmer')
        self.assertEqual(list(self.f.codes())[0], 0)

        self.assertEqual(list(self.f.value_labels())[0],
                         ('Programmer', 'Programmer'))
        self.assertEqual(list(self.f.coded_values())[0], (0, 'Programmer'))
        self.assertEqual(list(self.f.coded_labels())[0], (0, 'Programmer'))

    def test_random(self):
        values = self.f.values()
        random_values = self.f.random(3)

        self.assertEqual(len(random_values), 3)

        for val in random_values:
            self.assertTrue(val in values)


class DataFieldManagerTestCase(TestCase):
    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')

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
        self.assertEqual(
            [x.pk for x in DataField.objects.published(user1)], [7])
        # `user2` is not assigned
        self.assertEqual(
            [x.pk for x in DataField.objects.published(user2)], [])


class DataConceptTestCase(TestCase):
    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)

    def test_format(self):
        name_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'name')
        salary_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        boss_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'boss')

        concept = DataConcept(name='Title')
        concept.save()

        DataConceptField(concept=concept, field=name_field, order=1).save()
        DataConceptField(concept=concept, field=salary_field, order=2).save()
        DataConceptField(concept=concept, field=boss_field, order=3).save()

        values = ['CEO', 100000, True]

        self.assertEqual(
            concept.format(values),
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
                    'profile': '<span>' +
                               '</span><span>'.join(fvalues.values()) +
                               '</span>'
                })
            to_html.process_multiple = True

        formatters.register(HtmlFormatter, 'HTML')
        concept.formatter_name = 'HTML'

        self.assertEqual(
            concept.format(values, preferred_formats=['html']),
            OrderedDict([
                ('profile',
                 u'<span>CEO</span><span>100000</span><span>True</span>')
            ]))


class DataConceptManagerTestCase(TestCase):
    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)
        self.is_manager = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        DataCategory(published=False).save()
        self.category = DataCategory.objects.get(pk=1)

    def test_published(self):
        concept = DataConcept(published=True)
        concept.save()
        DataConceptField(concept=concept, field=self.is_manager).save()
        DataConceptField(concept=concept, field=self.salary).save()

        self.assertEqual([x.pk for x in DataConcept.objects.published()], [])

        self.is_manager.published = True
        self.is_manager.save()
        self.salary.published = True
        self.salary.save()

        # Now published, it will appear
        self.assertEqual([x.pk for x in DataConcept.objects.published()], [1])

        # Set the category to be an unpublished category and it should no
        # longer appear.
        concept.category = self.category
        concept.save()
        self.assertEqual([x.pk for x in DataConcept.objects.published()], [])

        # Publish the category and the concept should appear again
        self.category.published = True
        self.category.save()
        self.assertEqual([x.pk for x in DataConcept.objects.published()], [1])

        user1 = User.objects.create_user('user1', 'user1')

        # Nothing since user1 cannot view either datafield
        self.assertEqual(
            [x.pk for x in DataConcept.objects.published(user1)], [])

        assign('avocado.view_datafield', user1, self.is_manager)
        # Still nothing since user1 has no permission for salary
        self.assertEqual(
            [x.pk for x in DataConcept.objects.published(user1)], [])

        assign('avocado.view_datafield', user1, self.salary)
        # Now user1 can see the concept
        self.assertEqual(
            [x.pk for x in DataConcept.objects.published(user1)], [1])

        user2 = User.objects.create_user('user2', 'user2')

        # `user2` is not assigned
        self.assertEqual(
            [x.pk for x in DataConcept.objects.published(user2)], [])

        # Remove the fields from the concept and it should no longer appear
        # as published.
        DataConceptField.objects.filter(concept=concept).delete()
        self.assertEqual([x.pk for x in DataConcept.objects.published()], [])


class DataContextTestCase(TestCase):
    def test_init(self):
        json = {
            'field': 'tests.title.salary',
            'operator': 'gt',
            'value': '1000'
        }
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
    existing_email = 'existing@email.com'
    existing_username = 'user1'
    emails = [existing_email, 'new1@email.com', 'new2@email.com',
              'new3@email.com']
    usernames = [existing_username, 'user3', 'user4', 'user5', 'user6']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', publish=False,
                                concepts=False, quiet=True)
        f1 = DataField.objects.get(pk=1)
        f2 = DataField.objects.get(pk=2)

        c1 = DataConcept()
        c1.save()

        DataConceptField(concept=c1, field=f1).save()
        DataConceptField(concept=c1, field=f2).save()

    def test_init(self):
        json = {
            'context': {
                'field': 'tests.title.salary',
                'operator': 'gt',
                'value': '1000'
            },
            'view': {'columns': []}
        }

        query = DataQuery(json)
        self.assertEqual(query.context_json, json['context'])
        self.assertEqual(query.view_json, json['view'])

        # Test the json of the DataQuery properties too
        self.assertEqual(query.context.json, json['context'])
        self.assertEqual(query.view.json, json['view'])

        self.assertEqual(query.json, json)

    def test_multiple_json_values(self):
        json = {
            'context': {
                'field': 'tests.title.salary',
                'operator': 'gt',
                'value': '1000'
            },
            'view': {'columns': []}
        }
        context_json = {
            'context_json': {
                'field': 'tests.title.salary',
                'operator': 'gt',
                'value': '1000'
            },
        }
        view_json = {
            'view_json': {'columns': []}
        }

        self.assertRaises(TypeError, DataQuery, json, **context_json)
        self.assertRaises(TypeError, DataQuery, json, **view_json)

    def test_validate(self):
        attrs = {
            'context': {
                'field': 'tests.title.name',
                'operator': 'exact',
                'value': 'CEO',
                'language': 'Name is CEO'
            },
            'view': {
                'columns': [1],
            }
        }

        exp_attrs = deepcopy(attrs)
        exp_attrs['view'] = [{'concept': 1}]

        self.assertEqual(DataQuery.validate(deepcopy(attrs), tree=Employee),
                         exp_attrs)

    def test_parse(self):
        attrs = {
            'context': {
                'type': 'and',
                'children': [{
                    'field': 'tests.title.name',
                    'operator': 'exact',
                    'value': 'CEO',
                }]
            },
            'view': {
                'ordering': [(1, 'desc')]
            }
        }

        query = DataQuery(attrs)
        node = query.parse(tree=Employee)
        self.assertEqual(str(node.datacontext_node.condition),
                         "(AND: ('title__name__exact', u'CEO'))")
        self.assertEqual(str(node.dataview_node.ordering), "[(1, 'desc')]")

    def test_apply(self):
        attrs = {
            'context': {
                'field': 'tests.title.boss',
                'operator': 'exact',
                'value': True
            },
            'view': {
                'columns': [1],
            }
        }
        query = DataQuery(attrs)

        self.assertEqual(
            unicode(query.apply(tree=Employee).query),
            'SELECT DISTINCT "tests_employee"."id", '
            '"tests_office"."location", "tests_title"."name" FROM '
            '"tests_employee" INNER JOIN "tests_title" ON '
            '("tests_employee"."title_id" = "tests_title"."id") INNER JOIN '
            '"tests_office" ON ("tests_employee"."office_id" = '
            '"tests_office"."id") WHERE "tests_title"."boss" = True ')

        query = DataQuery({'view': {'ordering': [(1, 'desc')]}})
        queryset = Employee.objects.all().distinct()
        self.assertEqual(
            unicode(query.apply(queryset=queryset).query),
            'SELECT DISTINCT "tests_employee"."id", '
            '"tests_office"."location", "tests_title"."name" FROM '
            '"tests_employee" INNER JOIN "tests_office" ON '
            '("tests_employee"."office_id" = "tests_office"."id") LEFT OUTER '
            'JOIN "tests_title" ON ("tests_employee"."title_id" = '
            '"tests_title"."id") ORDER BY "tests_office"."location" DESC, '
            '"tests_title"."name" DESC')

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

    @override_settings(AVOCADO_SHARE_BY_USERNAME=True,
                       AVOCADO_SHARE_BY_USERNAME_CASE_SENSITIVE=True)
    def test_add_shared_user(self):
        # Make sure we are starting with the anticipated number of users.
        self.assertEqual(User.objects.count(), 1)

        # Assign an email to the existing user
        User.objects.update(email=self.existing_email,
                            username=self.existing_username)

        query = DataQuery(template=True, default=True)
        query.save()

        self.assertEqual(query.shared_users.count(), 0)
        # Try add an existing user to shared users by username
        query.share_with_user(self.existing_username)
        self.assertEqual(query.shared_users.count(), 1)

        [query.share_with_user(e) for e in self.emails]

        # Looking up non existant users with usernames should not
        # create new users
        [query.share_with_user(u) for u in self.usernames]

        # Check that the user count increased for the email-based users
        # and no extra users were created when queried w/ username
        self.assertEqual(User.objects.count(), 4)

        # Check that the users are in the query's shared_users
        self.assertEqual(query.shared_users.count(), 4)

    def test_duplicate_share(self):
        query = DataQuery(template=True, default=True)
        query.save()

        [query.share_with_user(e) for e in self.emails]

        share_count = query.shared_users.count()
        user_count = User.objects.count()

        # Make sure that requests to share with users that are already shared
        # with don't cause new user or shared_user entries.
        [query.share_with_user(e) for e in self.emails]

        self.assertEqual(share_count, query.shared_users.count())
        self.assertEqual(user_count, User.objects.count())

    @override_settings(AVOCADO_SHARE_BY_USERNAME=False,
                       AVOCADO_SHARE_BY_EMAIL=False)
    def test_no_create_on_share(self):
        # Make sure we are starting with the anticipated number of users.
        self.assertEqual(User.objects.count(), 1)

        # Assign an email to the existing user
        User.objects.all().update(email=self.existing_email)

        query = DataQuery(template=True, default=True)
        query.save()

        self.assertEqual(query.shared_users.count(), 0)

        # Test when both settings are False
        response = query.share_with_user(self.existing_email)
        self.assertEqual(response, False)

        with self.settings(AVOCADO_SHARE_BY_EMAIL=True):
            # Share with all the emails but, with create_user set to False, the
            # query should only be shared with the 1 existing user.
            [query.share_with_user(e, create_user=False)
                for e in self.emails]
            # Check that the user count increased for the email-based users
            self.assertEqual(User.objects.count(), 1)

            # Check that the users are in the query's shared_users
            self.assertEqual(query.shared_users.count(), 1)

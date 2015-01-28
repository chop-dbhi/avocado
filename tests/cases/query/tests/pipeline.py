from django.core import management
from django.test import TestCase
from avocado.query.pipeline import QueryProcessor
from avocado.models import DataConcept, DataView
from tests.models import Employee


class QueryProcessorTestCase(TestCase):
    fixtures = ['tests/fixtures/employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

        # The init command creates concepts named after the fields
        # by default.
        c = DataConcept.objects.get(name='First Name')

        self.v = DataView(json=[{'concept': c.pk}])

    def test(self):
        p = QueryProcessor(view=self.v, tree=Employee)
        q = p.get_queryset()

        i = p.get_iterable(queryset=q)

        self.assertEqual(len(list(i)), 6)

    def test_none_pre(self):
        p = QueryProcessor(view=self.v, tree=Employee)

        # Pass in an empty queryset
        q = p.get_queryset(queryset=Employee.objects.none())

        # Pass in an empty form this queryset
        i = p.get_iterable(queryset=q)

        self.assertEqual(len(list(i)), 0)

    def test_none_post(self):
        p = QueryProcessor(view=self.v, tree=Employee)

        # Change to an empty queryset
        q = p.get_queryset().none()

        i = p.get_iterable(queryset=q)

        self.assertEqual(len(list(i)), 0)

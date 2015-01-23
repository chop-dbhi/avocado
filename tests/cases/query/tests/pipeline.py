from django.core import management
from django.test import TransactionTestCase
from tests.models import Employee
from avocado.query.pipeline import Query


class QueryTestCase(TransactionTestCase):
    def test(self):
        management.call_command('loaddata',
                                'tests/fixtures/employee_data.json',
                                database='postgres')

        # Queryset to non-in-memory database
        queryset = Employee.objects.using('postgres')

        query = Query(queryset, name='test')

        # Create the iterator
        it = iter(query)

        # Get a result which executes the query
        result = next(it)
        self.assertIsNotNone(result)

        # Cancel
        self.assertTrue(query.cancel())

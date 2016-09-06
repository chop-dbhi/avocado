import time
from threading import Thread

from django.conf import settings
from django.core import management
from django.db import connections, DatabaseError
from django.test import TransactionTestCase, RequestFactory
from rq.job import JobStatus

from avocado.async import utils as async_utils
from avocado.models import DataContext, DataField, DataView
from avocado.query import utils
from tests.models import Employee
from tests.processors import ManagerQueryProcessor


class TempConnTest(TransactionTestCase):
    def _load_fixture(self, db):
        management.call_command('loaddata',
                                'tests/fixtures/employee_data.json',
                                database=db,
                                verbosity=0)

    def run_utils_test(self, db, name):
        self._load_fixture(db)

        conn = utils.named_connection(name, db=db)

        # Ensure it is stored and the settings are identical
        self.assertTrue(conn.alias in connections)
        self.assertEqual(conn.settings_dict, connections[db].settings_dict)

        _db, pid = utils._conn_info(name)

        # Connection info stored in cache
        self.assertEqual(db, _db)
        self.assertIsNotNone(pid)

        # Execute a query using the specified database.
        queryset = Employee.objects.using(conn.alias)
        self.assertEqual(queryset.db, conn.alias)

        self.assertEqual(queryset.count(), 6)

        utils.close_connection(name)

        # Cleaned up
        self.assertFalse(conn.alias in connections.databases)

        return conn

    def run_cancel_test(self, runner, stopper):
        t1 = Thread(target=runner, args=(self, self.db, self.name))
        t2 = Thread(target=stopper, args=(self, self.db, self.name))

        t1.start()

        # Delay so the query starts running.
        time.sleep(1)

        t2.start()

        # Block until the threads have finished.
        t1.join()
        t2.join()

        # Canceling again should be a no-op....
        self.assertIsNone(utils.cancel_query(self.name))

        # Ensure a new working connection can be opened under the
        # same named.
        conn = utils.named_connection(self.name, db=self.db)
        c = conn.cursor()
        c.execute('SELECT (1)')
        val, = c.fetchone()

        self.assertEqual(val, 1)


if 'sqlite' in settings.DATABASES:
    class SQLiteTempConnTest(TempConnTest):
        db = 'sqlite'
        name = 'test_sqlite'

        def test(self):
            self.run_utils_test(self.db, self.name)

        def test_cancel(self):
            # Hack to cause SQLite to sleep
            # http://stackoverflow.com/a/23758390/407954
            def runner(t, db, name):
                conn = utils.named_connection(name, db=db)
                conn.connection.create_function('sleep', 1, time.sleep)
                c = conn.cursor()
                c.execute("SELECT sleep(2)")

            def stopper(t, db, name):
                canceled = utils.cancel_query(name)
                t.assertTrue(canceled)

            self.run_cancel_test(runner, stopper)


if 'postgres' in settings.DATABASES:
    class PostgresTempConnTest(TempConnTest):
        db = 'postgres'
        name = 'test_postgres'

        def test(self):
            self.run_utils_test(self.db, self.name)

        def test_cancel(self):
            def runner(t, db, name):
                conn = utils.named_connection(name, db=db)
                c = conn.cursor()
                t.assertRaises(DatabaseError, c.execute, 'SELECT pg_sleep(2)')

            def stopper(t, db, name):
                canceled = utils.cancel_query(name)
                t.assertTrue(canceled)

            self.run_cancel_test(runner, stopper)


if 'mysql' in settings.DATABASES:
    class MySQLTempConnTest(TempConnTest):
        db = 'mysql'
        name = 'test_mysql'

        def test(self):
            self.run_utils_test(self.db, self.name)

        def test_cancel(self):
            def runner(t, db, name):
                conn = utils.named_connection(name, db=db)
                c = conn.cursor()
                c.execute('SELECT sleep(2)')

            def stopper(t, db, name):
                canceled = utils.cancel_query(name)
                t.assertTrue(canceled)

            self.run_cancel_test(runner, stopper)


class AsyncResultRowTestCase(TransactionTestCase):
    fixtures = ['tests/fixtures/employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)
        # Don't start with any jobs in the queue.
        async_utils.cancel_all_jobs()

    def tearDown(self):
        # Don't leave any jobs in the queue.
        async_utils.cancel_all_jobs()

    def test_create_and_cancel(self):
        # Create 3 meaningless jobs. We're just testing job setup and
        # cancellation here, not the execution.
        utils.async_get_result_rows(None, None, {})
        job_options = {
            'name': 'Job X',
        }
        job_x_id = utils.async_get_result_rows(None, None, {}, job_options)
        job_options = {
            'name': 'Job Y',
            'query_name': 'job_y_query',
        }
        job_y_id = utils.async_get_result_rows(None, None, {}, job_options)

        self.assertEqual(async_utils.get_job_count(), 3)

        jobs = async_utils.get_jobs()
        self.assertEqual(len(jobs), 3)

        job_x = async_utils.get_job(job_x_id)
        self.assertTrue(job_x in jobs)
        self.assertEqual(job_x.meta['name'], 'Job X')

        self.assertEqual(async_utils.cancel_job(job_x_id), None)
        self.assertEqual(async_utils.get_job_count(), 2)
        async_utils.cancel_job('invalid_id')
        self.assertEqual(async_utils.get_job_count(), 2)

        self.assertTrue('canceled' in async_utils.cancel_job(job_y_id))
        self.assertTrue(async_utils.get_job_count(), 1)

        async_utils.cancel_all_jobs()
        self.assertEqual(async_utils.get_job_count(), 0)

    def test_job_result(self):
        context = DataContext()
        view = DataView()
        limit = 3
        query_options = {
            'limit': limit,
            'page': 1,
        }
        request = RequestFactory().get('/some/request')

        job_id = utils.async_get_result_rows(context, view, query_options,
                                             request=request)
        self.assertTrue(async_utils.get_job_count(), 1)
        async_utils.run_jobs()
        time.sleep(1)
        result = async_utils.get_job_result(job_id)
        self.assertEqual(async_utils.get_job(job_id).status,
                         JobStatus.FINISHED)
        self.assertEqual(len(result['rows']), limit)
        self.assertEqual(result['limit'], limit)


class ResultRowTestCase(TransactionTestCase):
    fixtures = ['tests/fixtures/employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

    def test_invalid_options(self):
        # Page numbers less than 1 should not be allowed.
        query_options = {
            'page': 0,
        }
        self.assertRaises(ValueError,
                          utils.get_result_rows,
                          None,
                          None,
                          query_options)

        # Stop pages before start pages should not be allowed.
        query_options = {
            'page': 5,
            'stop_page': 1,
        }
        self.assertRaises(ValueError,
                          utils.get_result_rows,
                          None,
                          None,
                          query_options)

    def test_get_rows(self):
        context = DataContext()
        view = DataView()

        # Unless we tell the function to evaluate the rows, it should return
        # rows as a generator so we need to exclicitly evaluate it here.
        result = utils.get_result_rows(context, view, {})
        self.assertEqual(len(list(result['rows'])), Employee.objects.count())

        # Now, have the method evaluate the rows.
        result = utils.get_result_rows(context, view, {}, evaluate_rows=True)
        self.assertEqual(len(result['rows']), Employee.objects.count())

    def test_get_order_only(self):
        field = DataField.objects.get(field_name='salary')
        concept = field.concepts.all()[0]

        context = DataContext()
        view = DataView(json=[{
            'concept': concept.pk,
            'visible': False,
            'sort': 'desc',
        }])
        result = utils.get_result_rows(context, view, {})
        self.assertEqual(len(list(result['rows'])), Employee.objects.count())

    def test_limit(self):
        context = DataContext()
        view = DataView()
        limit = 2
        query_options = {
            'limit': limit,
            'page': 1,
        }
        result = utils.get_result_rows(context, view, query_options)
        self.assertEqual(len(list(result['rows'])), limit)
        self.assertEqual(result['limit'], limit)

    def test_processor(self):
        context = DataContext()
        view = DataView()
        processor = 'manager'
        query_options = {
            'processor': processor,
        }
        result = utils.get_result_rows(context, view, query_options)
        self.assertEqual(len(list(result['rows'])),
                         Employee.objects.filter(is_manager=True).count())
        self.assertTrue(isinstance(result['processor'], ManagerQueryProcessor))

    def test_export_type(self):
        context = DataContext()
        view = DataView()
        export_type = 'json'
        query_options = {
            'export_type': export_type,
        }
        result = utils.get_result_rows(context, view, query_options)
        self.assertEqual(len(list(result['rows'])), Employee.objects.count())
        self.assertEqual(result['export_type'], export_type)

    def test_pages(self):
        context = DataContext()
        view = DataView()
        query_options = {
            'page': 1,
            'stop_page': 10,
        }
        result = utils.get_result_rows(context, view, query_options)
        self.assertEqual(len(list(result['rows'])), Employee.objects.count())

        query_options = {
            'page': 1,
            'stop_page': 1,
        }
        result = utils.get_result_rows(context, view, query_options)
        self.assertEqual(len(list(result['rows'])), Employee.objects.count())

import time
from threading import Thread
from django.db import connections, OperationalError
from django.test import TransactionTestCase
from django.core import management
from tests.models import Employee
from avocado.query import utils


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
        self.assertFalse(conn.alias in connections._databases)

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


class PostgresTempConnTest(TempConnTest):
    db = 'postgres'
    name = 'test_postgres'

    def test(self):
        self.run_utils_test(self.db, self.name)

    def test_cancel(self):
        def runner(t, db, name):
            conn = utils.named_connection(name, db=db)
            c = conn.cursor()
            t.assertRaises(OperationalError, c.execute, 'SELECT pg_sleep(2)')

        def stopper(t, db, name):
            canceled = utils.cancel_query(name)
            t.assertTrue(canceled)

        self.run_cancel_test(runner, stopper)


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

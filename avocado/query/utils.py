import logging
import django
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.cache import cache

logger = logging.getLogger(__name__)


TEMP_DB_ALIAS_PREFIX = '_db:{0}'


def ensure_connection(conn):
    if django.VERSION < (1, 6):
        conn.cursor()
    else:
        conn.ensure_connection()


def isolate_queryset(name, queryset):
    """Creates a temporary named connection and binds a queryset.

    All QuerySets derived from this one will be executed using this connection.
    """
    queryset = queryset._clone()
    conn = named_connection(name, queryset.db)

    # Set to new database alias
    queryset._db = conn.alias
    queryset.query.using = conn.alias

    return queryset


def named_connection(name, db=DEFAULT_DB_ALIAS):
    """Initializes a named connection to a database.

    Django shares open connections to a database that exist in the same
    thread. This is not appropriate for potentially long-running queries
    which may need to be canceled.

    This function creates a new connection to a database using the same
    options defined in the database settings.

    Note: Adding the connection to django.db.connections is required
    because only database aliases are referenced in QuerySets, not the
    connection itself. When the QuerySet is *executed*, the alias is used
    to get the connection which must be present.
    """
    # Define a new database alias.
    temp_db = TEMP_DB_ALIAS_PREFIX.format(name)

    if temp_db in connections.databases:
        conn = connections[temp_db]

        if conn.is_dirty():
            raise KeyError('Connection {0} is in use.'.format(name))
    else:
        # Get the settings of the real database being connected to.
        connections.ensure_defaults(db)
        settings = connections.databases[db]

        # Add new database entry into connections handler so when the query
        # executes the new connection will be accessible.
        connections.databases[temp_db] = settings

        conn = connections[temp_db]

    # Get the backend specific process ID for the query. This opens the
    # connection to the database.
    pid = _get_backend_pid(conn)

    # Put real database alias and PID in centralized cache so multiple threads
    # and/or processes can access it.
    cache.set(temp_db, (db, pid))

    return conn


def cancel_query(name):
    "Cancels a query running on a named connection."
    temp_db = TEMP_DB_ALIAS_PREFIX.format(name)

    info = cache.get(temp_db)

    # Cancel the query if the cache entry is present.
    if info is not None:
        db, pid = info
        canceled = _cancel_query(name, db, pid)
    else:
        canceled = None

    if canceled:
        cache.delete(temp_db)

    close_connection(name)

    return canceled


def close_connection(name):
    "Closes a temporary connection by name and removes it from the handler."
    temp_db = TEMP_DB_ALIAS_PREFIX.format(name)

    # Remove connection from handler if in the same thread.
    if temp_db in connections.databases:
        conn = connections[temp_db]
        ensure_connection(conn)
        conn.close()

        del connections.databases[temp_db]


def _get_backend_pid(conn):
    "Gets the backend specific process or query ID for a connection."
    engine = conn.settings_dict['ENGINE']

    # Backend connections are lazily initialized, so ensure it's connected
    # before using internal method calls.
    ensure_connection(conn)

    # SQLite does not return a process id, so we use 0 as the non-None value.
    if engine == 'django.db.backends.sqlite3':
        return 0

    if engine == 'django.db.backends.postgresql_psycopg2':
        return conn.connection.get_backend_pid()

    if engine == 'django.db.backends.mysql':
        return conn.connection.thread_id()

    logger.warn('getting PIDs for {0} is not supported'.format(engine))


def _conn_info(name):
    temp_db = TEMP_DB_ALIAS_PREFIX.format(name)
    return cache.get(temp_db)


def _cancel_query(name, db, pid):
    """Cancels a query using backend specific methods.

    Note that the default connection is used to cancel the query, not the
    named connection (that is blocking).
    """
    conn = connections[db]
    engine = conn.settings_dict['ENGINE']

    if engine == 'django.db.backends.postgresql_psycopg2':
        c = conn.cursor()
        c.execute('SELECT pg_terminate_backend(%s)', (pid,))
        canceled, = c.fetchone()
        return canceled

    if engine == 'django.db.backends.mysql':
        c = conn.cursor()

        # Kills the query, but not the connection. Owners of the thread
        # are allowed to kill their own queries.
        c.execute('KILL QUERY %s', (pid,))

        # TODO; any way to confirm it was actually killed?
        # > SELECT 1 FROM information_schema.processlist WHERE id = %s
        # This query requires privileges..
        return True

    # SQLite can use any connection since it is serverless. It has a native
    # method to perform the interrupt.
    if engine == 'django.db.backends.sqlite3':
        ensure_connection(conn)
        conn.connection.interrupt()
        return True

    logger.warn('canceling queries for {0} is not supported'.format(engine))

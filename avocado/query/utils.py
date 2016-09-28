import logging

import django
from django.core.cache import get_cache
from django.db import connections, DEFAULT_DB_ALIAS, DatabaseError
from django_rq import get_queue

from avocado.conf import settings
from avocado.export import HTMLExporter, registry as exporters
from avocado.query import pipeline


logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 20
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
        logger.debug('reusing connection for %s', name)
    else:
        # Get the settings of the real database being connected to.
        connections.ensure_defaults(db)

        # Add new database entry into connections handler so when the query
        # executes the new connection will be accessible.
        connections.databases[temp_db] = connections.databases[db]

        conn = connections[temp_db]
        logger.debug('initializing connection for %s', name)

    # Get the backend specific process ID for the query. This will open a
    # connection to the database if not already open.
    pid = _get_backend_pid(conn)

    # Put real database alias and PID in centralized cache so multiple threads
    # and/or processes can access it.
    cache = get_cache(settings.QUERY_CACHE)
    cache.set(temp_db, (db, pid))

    return conn


def cancel_query(name):
    "Cancels a query running on a named connection."
    temp_db = TEMP_DB_ALIAS_PREFIX.format(name)

    cache = get_cache(settings.QUERY_CACHE)
    info = cache.get(temp_db)
    canceled = None

    # Cancel the query if the cache entry is present.
    if info is not None:
        logger.debug('canceling query on connection %s', name)
        db, pid = info
        canceled = _cancel_query(name, db, pid)

    # Clean up the connection.
    close_connection(name)

    return canceled


def close_connection(name):
    "Closes a temporary connection by name and removes it from the handler."
    temp_db = TEMP_DB_ALIAS_PREFIX.format(name)

    # Remove the cache entry.
    cache = get_cache(settings.QUERY_CACHE)
    cache.delete(temp_db)

    # Remove connection from handler if in the same thread.
    if temp_db in connections.databases:
        logger.debug('closing connection %s', name)

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
    cache = get_cache(settings.QUERY_CACHE)
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

        # Postgres will raise a database error if an unprivileged user
        # attempts to cancel a query that no longer exists.
        try:
            c.execute('SELECT pg_terminate_backend(%s)', (pid,))
        except DatabaseError:
            return

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


def get_exporter_class(export_type):
    """
    Returns the exporter class for the supplied export type name.

    Args:
        export_type(string): The string name of the exporter.

    Returns:
        The exporter class for the supplied exporter_type as defined in
        the exporters registry. See avocado.export.registry for more info.
    """
    if export_type.lower() == 'html':
        return HTMLExporter

    return exporters[export_type]


def async_get_result_rows(context, view, query_options, job_options=None,
                          request=None):
    """
    Creates a new job to asynchronously get result rows and returns the job ID.

    Args:
        See get_result_rows argument list.

    Keyword Arugments:
        Set as properties on the returned job's meta.

    Returns:
        The ID of the created job.
    """
    offset = None

    page = query_options.get('page')
    limit = query_options.get('limit') or 0
    stop_page = query_options.get('stop_page')
    query_name = query_options.get('query_name')
    processor_name = query_options.get('processor') or 'default'
    tree = query_options.get('tree')
    export_type = query_options.get('export_type') or 'html'
    reader = query_options.get('reader')

    if page is not None:
        page = int(page)

        # Pages are 1-based.
        if page < 1:
            raise ValueError('Page must be greater than or equal to 1.')

        # Change to 0-base for calculating offset.
        offset = limit * (page - 1)

        if stop_page:
            stop_page = int(stop_page)

            # Cannot have a lower index stop page than start page.
            if stop_page < page:
                raise ValueError(
                    'Stop page must be greater than or equal to start page.')

            # 4...5 means 4 and 5, not everything up to 5 like with
            # list slices, so 4...4 is equivalent to just 4
            if stop_page > page:
                limit = limit * stop_page
    else:
        # When no page or range is specified, the limit does not apply.
        limit = None

    QueryProcessor = pipeline.query_processors[processor_name]
    processor = QueryProcessor(context=context, view=view, tree=tree)
    queryset = processor.get_queryset(request=request)

    # Isolate this query to a named connection. This will cancel an
    # outstanding queries of the same name if one is present.
    cancel_query(query_name)
    queryset = isolate_queryset(query_name, queryset)

    # 0 limit means all for pagination, however the read method requires
    # an explicit limit of None
    limit = limit or None

    if limit:
        queryset = queryset[:limit]

    sql, params = queryset.query.get_compiler(queryset.db).as_sql()

    if not job_options:
        job_options = {}

    queue = get_queue(settings.ASYNC_QUEUE)

    job = queue.enqueue(get_and_format_rows,
                        sql=sql,
                        params=params,
                        processor_name=processor_name,
                        context=context,
                        view=view,
                        page=page,
                        stop_page=stop_page,
                        tree=tree,
                        offset=offset,
                        limit=limit,
                        export_type=export_type,
                        reader=reader,
                        queryset=queryset,
                        db=queryset.db)

    job.meta.update(job_options)
    job.save()

    return job.id


def get_and_format_rows(sql, params, processor_name, context, view, tree,
                        page, stop_page, offset, limit, export_type, reader,
                        db, queryset):

    QueryProcessor = pipeline.query_processors[processor_name]
    processor = QueryProcessor(context=context, view=view, tree=tree)

    # We use HTMLExporter in Serrano but Avocado has it disabled. Until it
    # is enabled in Avocado, we can reference the HTMLExporter directly here.
    exporter = processor.get_exporter(get_exporter_class(export_type))

    conn = connections[db]
    cur = conn.cursor()
    cur.execute(sql, params)

    view_node = view.parse()

    # This is an optimization when concepts are selected for ordering
    # only. There is no guarantee to how many rows are required to get
    # the desired `limit` of rows, so the query is unbounded. If all
    # ordering facets are visible, the limit and offset can be pushed
    # down to the query.
    order_only = lambda f: not f.get('visible', True)

    if filter(order_only, view_node.facets):
        rows = exporter.manual_read(cur,
                                    offset=offset,
                                    limit=limit)
    else:
        method = exporter.reader(reader)
        rows = method(cur)

    rows = list(rows)

    return {
        'context': context,
        'export_type': export_type,
        'limit': limit,
        'offset': offset,
        'page': page,
        'processor': processor,
        'queryset': queryset,
        'rows': rows,
        'stop_page': stop_page,
        'view': view,
    }


def get_result_rows(context, view, query_options, evaluate_rows=False,
                    request=None):
    """
    Returns the result rows and options given the supplied arguments.

    The options include the exporter, queryset, offset, limit, page, and
    stop_page that were used when calculating the result rows. These can give
    some more context to callers of this method as far as the returned row
    set is concerned.

    Args:
        context (DataContext): Context for the query processor
        view (DataView): View for the query processor
        query_options (dict): Options for the query and result rows slice.
            These options include:
                * page: Start page of the result row slice.
                * limit: Upper bound on number of result rows returned.
                * stop_page: Stop page of result row slice.
                * query_name: Query name used when isolating result row query.
                * processor: Processor to use to generate queryset.
                * tree: Modeltree to pass to QueryProcessor.
                * export_type: Export type to use for result rows.
                * reader: Reader type to use when exporting, see
                    export._base.BaseExporter.readers for available readers.

    Kwargs:
        evaluate_rows (default=False): When this is True, the generator
            returned from the read method of the exporter will be evaluated
            and all results will be stored in a list. This is useful if the
            caller of this method actually needs an evaluated result set. An
            example of this is calling this method asynchronously which needs
            a pickleable return value(generators can't be pickled).
        request (default=None): Django request object to be passed to the
            QueryProcessor's get_queryset method. This allows a
            custom query processor to modify query handling based on request
            data such as the user.

    Returns:
        dict -- Result rows and relevant options used to calculate rows. These
            options include:
                * exporter: The exporter used.
                * limit: The limit on the number of result rows.
                * offset: The starting offset of the result rows.
                * page: The starting page number of the result rows.
                * queryset: The queryset used to gather results.
                * rows: The result rows themselves.
                * stop_page: The stop page of the result rows collection.

    """
    offset = None

    page = query_options.get('page')
    limit = query_options.get('limit') or 0
    stop_page = query_options.get('stop_page')
    query_name = query_options.get('query_name')
    processor_name = query_options.get('processor') or 'default'
    tree = query_options.get('tree')
    export_type = query_options.get('export_type') or 'html'
    reader = query_options.get('reader')

    if page is not None:
        page = int(page)

        # Pages are 1-based.
        if page < 1:
            raise ValueError('Page must be greater than or equal to 1.')

        # Change to 0-base for calculating offset.
        offset = limit * (page - 1)

        if stop_page:
            stop_page = int(stop_page)

            # Cannot have a lower index stop page than start page.
            if stop_page < page:
                raise ValueError(
                    'Stop page must be greater than or equal to start page.')

            # 4...5 means 4 and 5, not everything up to 5 like with
            # list slices, so 4...4 is equivalent to just 4
            if stop_page > page:
                limit = limit * stop_page
    else:
        # When no page or range is specified, the limit does not apply.
        limit = None

    QueryProcessor = pipeline.query_processors[processor_name]
    processor = QueryProcessor(context=context, view=view, tree=tree)
    queryset = processor.get_queryset(request=request)

    # Isolate this query to a named connection. This will cancel an
    # outstanding queries of the same name if one is present.
    cancel_query(query_name)
    queryset = isolate_queryset(query_name, queryset)

    # 0 limit means all for pagination, however the read method requires
    # an explicit limit of None
    limit = limit or None

    # We use HTMLExporter in Serrano but Avocado has it disabled. Until it
    # is enabled in Avocado, we can reference the HTMLExporter directly here.
    exporter = processor.get_exporter(get_exporter_class(export_type))

    # This is an optimization when concepts are selected for ordering
    # only. There is no guarantee to how many rows are required to get
    # the desired `limit` of rows, so the query is unbounded. If all
    # ordering facets are visible, the limit and offset can be pushed
    # down to the query.
    order_only = lambda f: not f.get('visible', True)
    view_node = view.parse()

    if filter(order_only, view_node.facets):
        iterable = processor.get_iterable(queryset=queryset)
        rows = exporter.manual_read(iterable,
                                    offset=offset,
                                    limit=limit)
    else:
        iterable = processor.get_iterable(queryset=queryset,
                                          limit=limit,
                                          offset=offset)
        method = exporter.reader(reader)
        rows = method(iterable)

    if evaluate_rows:
        rows = list(rows)

    return {
        'context': context,
        'export_type': export_type,
        'limit': limit,
        'offset': offset,
        'page': page,
        'processor': processor,
        'queryset': queryset,
        'rows': rows,
        'stop_page': stop_page,
        'view': view,
    }

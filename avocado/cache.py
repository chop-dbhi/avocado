import hashlib
import cPickle as pickle

from django.core.cache import cache

CACHE_CHUNK_SIZE = 100

class QueryStore(object):
    def _make_key(self, *args):
        p = pickle.dumps(args)
        return hashlib.md5(p).hexdigest()

    def _querykey(self, criteria, columns, ordering):
        return self._make_key(criteria, columns, ordering)

    def _datakey(self, criteria, columns, ordering, offset):
        return self._make_key(criteria, columns, ordering, offset)

    def get_datakeys(self, criteria, columns, ordering):
        querykey = self._querykey(criteria, columns, ordering)
        # the tups represents a list of pairs representing the 'offset' for that
        # slice of data and the corresponding 'datakey'
        return cache.get(querykey)

    def get(self, criteria, columns, ordering, offset, limit=CACHE_CHUNK_SIZE):
        """`key' refers to a 'query' key to see if any cache about that
        query is stored. `offset' refers to the starting point of the data.
        `limit' can vary since it is equivalent to a 'paginate by' behavior.
        """
        tups = self.get_datakeys(criteria, columns, ordering)
        # nothing stored about this query exists, return None to notify that
        # the query must be executed and the cache needs to be set.
        if tups is None:
            return
        # ensure that the limit is never over what is allowed
        end = offset + min(limit, CACHE_CHUNK_SIZE)
        if (end - offset) < 1:
            raise RuntimeError, 'a negative slice cannot be requested'

        # iterate over each slice
        for st_offset, datakey in tups:
            # the stored off end point will also be relative to the
            # CACHE_CHUNK_SIZE
            st_end = st_offset + CACHE_CHUNK_SIZE
            # cache hit!
            if st_offset <= offset < st_end and end <= st_end:
                return cache.get(datakey)

    def set(self, criteria, columns, ordering, offset, data):
        """Adds a slice of data if it doesn't already exist."""
        datakey = self._datakey(criteria, columns, ordering, offset)
        # set data prior to making it accessible, i.e. no race conditions
        cache.set(datakey, data)

        querykey = self._querykey(criteria, columns, ordering)
        tups = cache.get(querykey)
        # not yet set
        if tups is None:
            tups = set([])
        tups.add((offset, datakey))
        querykey
        # update the cache with additional tup
        cache.set(querykey, tups)

querystore = QueryStore()

from math import ceil

MAX_CACHED_ROW_LIMIT = 500


class InvalidPage(Exception):
    pass


class LazyPaginator(object):
    """The LazyPaginator is a simple class that provides the basic tools to
    compute the `start' and `end' indices for a given page. This can be useful
    when rolling out a standalone Paginagtor class for handling different
    data structures that could utilize pagination.

    >>> tests = (
    ...     (300, 20, 5, 100),
    ...     (0, 100, 2, 30),
    ...     (1000, 10, 10, 30),
    ...     (999, 5, 10, 50),
    ...     (12000, 50, 25, 1000),
    ...     (100, 10, 11, 0),
    ... )
    >>> for test in tests:
    ...     lp = LazyPaginator(count=test[0], paginate_by=test[1])
    ...     lp.page = test[2]
    ...     print lp.num_pages, lp.start_index, lp.end_index,
    ...     print lp.page_exists(test[3])
    15 80 99 False
    0 0 0 False
    100 90 99 True
    199 45 49 False
    240 1200 1249 True
    10 90 99 True
    """

    def __init__(self, count, paginate_by):
        self.count = max(0, count)
        self.paginate_by = max(1, int(paginate_by))
        self._page_cache = {}
        self._start_index = None
        self._end_index = None

    def _reset_attrs(self, page):
        if page in self._page_cache.keys():
            c = self._page_cache[page]
            self._start_index = c[0]
            self._end_index = c[1]
        else:
            self._start_index, self._end_index = None, None
            self._page_cache[page] = (self.start_index, self.end_index)

    def _get_num_pages(self):
        if not hasattr(self, '_num_pages'):
            if self.count == 0:
                self._num_pages = 0
            else:
                self._num_pages = int(ceil(self.count / self.paginate_by))
        return self._num_pages
    num_pages = property(_get_num_pages)

    def _get_start_index(self):
        if self._start_index is None:
            if self.count == 0:
                self._start_index = 0
            else:
                self._start_index = self.paginate_by * (min(self.num_pages, self.page) - 1)
        return self._start_index
    start_index = property(_get_start_index)

    def _get_end_index(self):
        if self._end_index is None:
            self._end_index = max(0, self.paginate_by * min(self.num_pages, self.page) - 1)
        return self._end_index
    end_index = property(_get_end_index)

    def _get_page(self):
        if not hasattr(self, '_page'):
            self._page = None
        return self._page

    def _set_page(self, page):
        page = int(page)
        if page < 1:
            raise InvalidPage, 'page numbers less than 1 are not valid'
        self._page = page
        self._reset_attrs(page)

    page = property(_get_page, _set_page) 

    def page_exists(self, offset, limit=MAX_CACHED_ROW_LIMIT):
        """Check whether the current slice of data is contained within another
        slice providing the `offset' and the `limit'.
        """
        if self.start_index >= offset and self.end_index <= (offset + limit - 1):
            return True
        return False



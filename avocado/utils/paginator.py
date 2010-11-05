import math

from django.core.paginator import Paginator, Page

class BufferedPaginator(Paginator):
    """A subclass of the Django Paginator class that allows for explicitly
    setting the ``_count`` attribute i.e. the theoretical size of
    ``object_list``. This removes the need for the Paginator to do determine
    the size of the ``object_list`` which improves performance especially for
    complex queries (and removes the need to actually pass in the
    ``objec_list``).

    The ``object_list`` that is passed in as an argument should represent the
    *buffered* part of the whole ``object_list``. This works in conjunction
    with the ``BufferedPage`` which can test whether or not a particular page
    is actually stored in the ``BufferedPaginator`` object.

    If ``object_list`` is not passed in, all calculations will still be
    available, but any operations that act on the ``object_list`` will
    throw an error, unless an ``object_list`` is passed in.

    The use of the class is primarily for large data sets in which it is
    impractical to store the entire ``object_list`` into a paginator.
    Overriding ``_count`` allows for the methods to still be used.

    ``buf_size`` represents the size of the buffer, i.e. number of rows that will
    be available at any given time and in most cases the size of ``object_list``
    assuming ``_count`` is greater than ``buf_size``..
    """
    def __init__(self, count, object_list=None, offset=0, buf_size=None, *args, **kwargs):
        if not object_list and not buf_size:
            raise ValueError, 'an "object_list" or a "buf_size" must be defined'
        if offset > count:
            raise ValueError, '"offset" cannot be greater than the "count"'

        super(BufferedPaginator, self).__init__(object_list, *args, **kwargs)

        self._count = count
        # negative offsets are relative to to ``count``
        if offset < 0:
            offset = count + offset
        self.offset = offset
        self.buf_size = buf_size or len(object_list)

    def page(self, number):
        """Returns a ``BufferedPage`` object representing the slice of data
        relative to the ``per_page`` number.
        """
        number = self.validate_number(number)

        if self.object_list:
            bottom = (number - 1) * self.per_page - self.offset

            if bottom < 0:
                bottom = 0

            top = bottom + self.per_page

            if top + self.orphans >= self.count:
                top = self.count

            object_list = self.object_list[bottom:top]
        elif self.object_list is not None:
            object_list = []
        else:
            object_list = None

        return BufferedPage(number, self, object_list)

    def cached_page_indices(self):
        "Returns the indices of the first and last pages that are cached."
        # the number of rows per page is greater than we will ever have in
        # the buffer at any given time. we can only provide partial results
        if self.buf_size < self.per_page:
            # the beginning items are missing.. no good
            if self.offset > 0:
                return (0, 0)

        pages_of_offset = math.ceil(self.offset / float(self.per_page))
        first = int(pages_of_offset) + 1
        last = first + math.ceil(self.buf_size / float(self.per_page))

        return (int(first), int(last))

    def cached_pages(self):
        first, last = self.cached_page_indices()
        return last - first

    def get_overlap(self, offset, buf_size=None):
        """Calculates the overlap of the buffered rows relative to a new offset
        and (optionally) buf_size. There are two sets of outputs here including
        the start and end terminals::

            [(start_offset, start_limit), (end_offset, end_limit)]

        The offsets and limits can be used for list slicing or for SQL OFFSET/
        LIMIT clauses.
        """
        buf_size = buf_size or self.buf_size

        overlap = True
        start_offset = start_limit = end_offset = end_limit = None

        # if the start terminal is within the current range, then there will be
        # a slice of data to be appended
        if self.offset <= offset <= (self.offset + self.buf_size):
            end_offset = (self.offset + self.buf_size) + 1
            end_limit = buf_size - (end_offset - offset) + 1

        # if the end terminal is within the current range, then there will be a
        # slice of data to be prepended
        elif self.offset <= (offset + buf_size) <= (self.offset + self.buf_size):
            start_offset = offset
            start_limit = self.offset - start_offset

        # check to see if the current range is within the start and end
        # terminals
        elif offset <= self.offset and (self.offset + self.buf_size) <= (offset + buf_size):
            start_offset = offset
            start_limit = self.offset - start_offset
            end_offset = (self.offset + self.buf_size) + 1
            end_limit = (offset + buf_size) - end_offset + 1

        # no overlap at all
        else:
            overlap = False
            start_offset = offset
            start_limit = buf_size

        return (overlap, (start_offset, start_limit), (end_offset, end_limit))


class BufferedPage(Page):
    """A subclass of the django Page class which adds an additional method to
    determine if this page is in cache. The determination is with respect to
    the `paginator' `offset' and `buf_size' attributes.
    """
    def __init__(self, number, paginator, object_list=None):
        self.number = number
        self.paginator = paginator
        self.object_list = object_list

    def in_cache(self):
        first, last = self.paginator.cached_page_indices()
        return first <= self.number < last

    def offset(self):
        return max(self.start_index(), 1) - 1

    def get_list(self, object_list=None):
        if object_list is not None:
            s = self.start_index() - self.paginator.offset - 1
            e = self.end_index() - self.paginator.offset
            return object_list[s:e]
        if self.object_list is not None:
            return self.object_list
        return None

    def page_links(self, before_after_count=2, first_last_count=0):
        pages = []
        # only process if the current page number is greater than the number of
        # required links.
        if self.number > (first_last_count + before_after_count + 1):
            # append first pages, e.g. [1, 2] if `first_last_count' is 2
            for i in range(1, first_last_count + 1):
                pages.append(i)

            pages.append(None)
            # append the leading pages relative to the current page, e.g.
            # [10, 11] if `before_after_count' is 2 and current page is 12
            for i in range(self.number - before_after_count, self.number):
                pages.append(i)

        else:
            for i in range(1, self.number):
                pages.append(i)

        # if there is still a gap until `self.paginator.num_pages' is reached, add trailing pages
        if (self.number + first_last_count + before_after_count) < self.paginator.num_pages:
            for i in range(self.number, self.number + before_after_count + 1):
                pages.append(i)

            pages.append(None)
            for i in range(self.paginator.num_pages + 1 - first_last_count, self.paginator.num_pages + 1):
                pages.append(i)

        else:
            for i in range(self.number, self.paginator.num_pages + 1):
                pages.append(i)

        return pages

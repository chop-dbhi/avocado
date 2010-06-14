import math

from django.core.paginator import Paginator, Page

class BufferedPaginator(Paginator):
    """A subclass of the django Paginator class that allows for explicitly
    setting the `_count' attribute i.e. the size of the `object_list'. This
    removes the need for the Paginator to do determine the size of the
    `object_list'.
    
    The `object_list' that is passed in as an argument represents the
    "buffered" part of intended `object_list'. This works in conjunction with
    the BufferedPage which can test whether or not the page is in "cache" (i.e
    within the BufferedPaginator `object_list').
    
    The use of the class is primarily for large data sets in which it is
    impractical to store into a Paginator. Overriding `_count' allows for the
    methods to still be used with the assumed value.
    """
    def __init__(self, count, offset, limit=None, *args, **kwargs):
        "Overrides `_count' to prevent a database hit."
        super(BufferedPaginator, self).__init__(*args, **kwargs)
        self._count = int(count)
        if offset < 0:
            offset = self._count + offset
        self.offset = offset
        self.limit = limit or len(self.object_list)

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page - self.offset

        if bottom < 0:
            bottom = 0

        top = bottom + self.per_page

        if top + self.orphans >= self.count:
            top = self.count

        return BufferedPage(self.object_list[bottom:top], number, self)
    
    def cached_page_indices(self):
        "Returns the indices of the first and last pages that are cached."
        
        # implies a partial page cache
        if self.limit < self.per_page:
            # the beginning items are missing.. no good
            if self.offset > 0:
                return (0, 0)

        pages_of_offset = math.ceil(self.offset / float(self.per_page))
        first = int(pages_of_offset) + 1
        last = first + math.ceil(self.limit / float(self.per_page))
        return (first, last)
    
    def cached_pages(self):
        first, last = self.cached_page_indices()
        return last - first

class BufferedPage(Page):
    """A subclass of the django Page class which adds an additional method to
    determine if this page is in cache. The determination is with respect to
    the `paginator' `offset' and `limit' attributes.
    """
    def __init__(self, object_list, number, paginator):
        self.number = number
        self.paginator = paginator
        if self.in_cache():
            self.object_list = object_list
        else:
            self.object_list = []

    def in_cache(self):
        first, last = self.paginator.cached_page_indices()
        return first <= self.number < last
    
    def start_index(self):
        if not self.in_cache():
            return None
        return super(BufferedPage, self).start_index()

    def end_index(self):
        if not self.in_cache():
            return None
        return super(BufferedPage, self).end_index()
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
    
    >>> params = [
    ... # count, offset, limit, items, paginate_by
    ... [100, 0, 10, [0, 1, 2, 3, 4, 5, 6, 7, 9, 10], 2],
    ... [100, 40, 10, [0, 1, 2, 3, 4, 5, 6, 7, 9, 10], 2],
    ... [20, 0, 10, [0, 1, 2, 3, 4, 5, 6, 7, 9, 10], 2],
    ... ]
    ...
    >>> for p in params:
    ...     bp = BufferedPaginator(*p)
    ...     bp.num_pages()
    ...     bp.page(1).in_cache()
    ...     bp.page(2).in_cache()
    ...     bp.page(5).in_cache()
    ...     bp.page(10).in_cache()
    ...
    50
    True
    True
    False
    False
    10
    True
    False
    False
    False
    
    """
    def __init__(self, count, offset, limit, *args, **kwargs):
        "Overrides `_count' to prevent a database hit."
        super(BufferedPaginator, self).__init__(*args, **kwargs)
        self.offset = offset
        self.limit = limit
        self._count = int(count)

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page - self.offset

        if bottom < 0:
            bottom = 0

        top = bottom + self.per_page

        if top + self.orphans >= self.count:
            top = self.count

        return BufferedPage(self.object_list[bottom:top], number, self)

class BufferedPage(Page):
    """A subclass of the django Page class which adds an additional method to
    determine if this page is in cache. The determination is with respect to
    the `paginator' `offset' and `limit' attributes.
    
    (doctests in BufferedPaginator class)
    """
    def in_cache(self):
        offset = self.paginator.offset
        limit = self.paginator.limit

        if (self.start_index() - 1) < offset:
            return False

        if (self.end_index() - 1) > (offset + limit):
            return False
        return True

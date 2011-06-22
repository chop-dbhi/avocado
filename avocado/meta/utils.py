def distribution(self, exclude=[], min_count=None, max_points=20,
    order_by='field', smooth=0.01, annotate_by='id', **filters):

    """Builds a GROUP BY queryset for use as a value distribution.

    ``exclude`` - a list of values to be excluded from the distribution. it
    may be desired to exclude NULL values or the empty string.

    .. note::

        the default behavior of the ``exclude`` argument is to do a SQL
        equivalent of NOT IN (...). if ``None`` is included, it will have
        a custom behavior of IS NOT NULL and will be removed from the IN
        clause. default is to include all values

    ``min_count`` - the minimum count for a particular value to be included
    in the distribution.

    ``max_points`` - the maximum number of points to be include in the
    distribution. the min and max values are always included, then a random
    sample is taken from the distribution. default is 30

    ``order_by`` - specify an ordering for the distribution. the choices are
    'count', 'field', or None. default is 'count'

    ``filters`` - a dict of filters to be applied to the queryset before
    the count annotation.
    """
    name = str(self.field_name)

    # get base queryset
    dist = self.model.objects.values(name)

    # exclude certain values (e.g. None, '')
    if exclude:
        exclude = set(exclude)
        kwargs = {}

        # special case for null values
        if None in exclude:
            kwargs['%s__isnull' % name] = True
            exclude.remove(None)

        kwargs['%s__in' % name] = exclude
        dist = dist.exclude(**kwargs)

    # apply filters before annotation is made
    if filters:
        dist = dist.filter(**filters)

    # apply annotation
    dist = dist.annotate(count=Count(annotate_by))

    if min_count is not None and min_count > 0:
        dist = dist.exclude(count__lt=min_count)

    # evaluate
    dist = dist.values_list(name, 'count')

    # apply ordering
    if order_by == 'count':
        dist = dist.order_by('count')
    elif order_by == 'field':
        dist = dist.order_by(name)

    dist = list(dist)

    if len(dist) < 3:
        return tuple(dist)

    minx = dist.pop(0)
    maxx = dist.pop()

    if self.datatype == 'number' and smooth > 0:
        maxy = dist[0][1]
        for x, y in dist[1:]:
            maxy = max(y, maxy)
        maxy = float(maxy)
        smooth_dist  = []
        for x, y in dist:
            if y / maxy >= smooth:
                smooth_dist.append((x, y))
        dist = smooth_dist

    if max_points is not None:
        # TODO faster to do count or len?
        dist_len = len(dist)
        step = int(dist_len/float(max_points))

        if step > 1:
            # we can safely assume that this is NOT categorical data when
            # ``max_points`` is set and/or the condition where the count will
            # be greater than max_points will usually never be true

            # sample by step value
            dist = dist[::step]

    dist.insert(0, minx)
    dist.append(maxx)

    return tuple(dist)


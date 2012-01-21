import math
from django.db.models import Count

FIRST_QUARTILE = 0.25
THIRD_QUARTILE = 0.75

def freedman_diaconis(queryset, count, field_name, smooth):
    """Builds a GROUP BY queryset for use as a value distribution. Data is
    binned according to a bin width specified by the Freedman-Diaconis Rule of:

        h = 2 * (IQR / n^(1/3))

    h = bin width, IQR = Interquartile range, n = number of observations.

    Citation: Freedman, David; Diaconis, Persi (December 1981). "On the
    histogram as a density estimator: L2 theory" Probability Theory and Related
    Fields 57 (4): 453-476. ISSN 0178-8951.
    """
    queryset = queryset.values_list(field_name, flat=True).order_by(field_name)

    q1_loc = int(math.floor(count * FIRST_QUARTILE)) - 1
    q3_loc = int(math.ceil(count * THIRD_QUARTILE)) - 1

    if q1_loc < 0:
        q1_loc = 0

    if q3_loc >= count:
        q3_loc = count - 1

    q1 = queryset[q1_loc]
    q3 = queryset[q3_loc]

    iqr = q3 - q1

    width = 2 * (float(iqr) * pow(count, -(1.0 / 3.0)))

    queryset = queryset.annotate(count=Count(field_name)).values_list(field_name, 'count')

    min_pt = queryset[0]
    max_pt = queryset.reverse()[0]

    if width == 0:
        median = queryset.order_by('-count')[0]
        dist = [min_pt, median, max_pt]
        seen = set()
        return [x for x in dist if x not in seen and not seen.add(x)]

    # initialize starting bin and bin height. create list for bins
    bins = []
    height = 0
    current_bin = float(min_pt[0]) + width

    for data_pt in queryset.iterator():
        # Minimum and Max are ignored for now and will be added later
        if data_pt == min_pt or data_pt == max_pt:
            continue

        pt = float(data_pt[0])

        # If data point is less than the current bin
        # add to the bin height
        if pt <= current_bin:
            height += data_pt[1]
        else:
            x = current_bin
            y = height
            prev = (0, 0)
            if bins:
                prev = bins.pop()

            # compare current bin to previous
            # if prev bin is small, the current bin takes in previous.
            # previous bin takes in current bin, if current bin is small
            if y > 0:
                if y * smooth > prev[1]:
                    fact = prev[1] / y
                    bin_x = x - (width / 2) - fact
                    bin_y = y + prev[1]
                    xy = (bin_x, bin_y)
                elif prev[1] * smooth > y:
                    fact = y / prev[1]
                    bin_x = prev[0] + fact
                    bin_y = y + prev[1]
                    xy = (bin_x, bin_y)
                else:
                    bins.append(prev)
                    bin_x = x - (width / 2)
                    xy = (bin_x, y)

                bins.append(xy)

            # reset the bin height after appending bin data
            height = 0

            # increment to next bin until data_pt
            # is within a bin. Add to height and
            # move to next data_pt
            if width == 0:
                return []

            while pt > current_bin:
                current_bin += width

            # Once a bin is found, add in the height
            height += data_pt[1]

    # Add back the min and max points and return the
    # list of X, Y coordinates.
    bins.insert(0, (float(min_pt[0]), min_pt[1]))
    bins.append((float(max_pt[0]), max_pt[1]))
    return bins

def distribution(queryset, field_name, datatype, exclude=[], order_by='field',
    smooth=0.01, annotate_by='id', **filters):
    """
    ``exclude`` - a list of values to be excluded from the distribution. it
    may be desired to exclude NULL values or the empty string.

    .. note::

        the default behavior of the ``exclude`` argument is to do a SQL
        equivalent of NOT IN (...). if ``None`` is included, it will have
        a custom behavior of IS NOT NULL and will be removed from the IN
        clause. default is to include all values

    ``order_by`` - specify an ordering for the distribution. the choices are
    'count', 'field', or None. default is 'count'

    ``smooth`` - smoothing facter that specifies how small a bin height can
    be compared to its neighboring bins

    ``filters`` - a dict of filters to be applied to the queryset before
    the count annotation.
    """
    # exclude certain values (e.g. None, '')
    if exclude:
        exclude = set(exclude)
        kwargs = {}

        # special case for null values
        if None in exclude:
            kwargs['%s__isnull' % field_name] = True
            exclude.remove(None)

        kwargs['%s__in' % field_name] = exclude
        queryset = queryset.exclude(**kwargs)

    # apply filters before annotation is made
    if filters:
        queryset = queryset.filter(**filters)

    count = queryset.count()
    # Nothing left to do
    if count == 0:
        return []

    # Apply binning algorithm for numerical data
    if datatype == 'number' and smooth >= 0:
        return freedman_diaconis(queryset, count, field_name, smooth)

    # Apply annotation
    queryset = queryset.annotate(count=Count(annotate_by))\
        .values_list(field_name, 'count')

    # Apply ordering relative to count or relative to the
    # field name (alphanumeric)
    if order_by == 'count':
        queryset = queryset.order_by('count')
    elif order_by == 'field':
        queryset = queryset.order_by(field_name)

    return tuple(queryset)

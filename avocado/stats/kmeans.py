import math
import random
from collections import defaultdict


def std_dev(values):
    """
    Computes the standard deviation of the 'values' list.

    TODO: Consider adding support for axes as in numpy and letting this method
    accept nested lists:
        http://docs.scipy.org/doc/numpy/reference/generated/numpy.std.html

    Arguments:
        values: list
            A list of numbers to compute the standard deviation of.

    Returns:
        The standard deviation of the elements in the 'values' list.
    """
    # Compute the mean
    mean = sum(values) / float(len(values))

    # Compute the square difference of all the values
    square_differences = [(v - mean) ** 2 for v in values]

    return math.sqrt(sum(square_differences) / float(len(square_differences)))


def is_iterable(obj):
    """
    Returns True if 'obj' is iterable and False otherwise.

    We check for __iter__ and for __getitem__ here because an iterable type
    must, by definition, define one of these attributes but is not required or
    guarenteed to define both of them. For more information on iterable types
    see:

        http://docs.python.org/2/glossary.html#term-iterable
        http://docs.python.org/2/library/functions.html#iter
    """
    return hasattr(obj, '__iter__') or hasattr(obj, '__getitem__')


def divide_by_scalar(lst, s):
    """
    Divides each element in 'lst' by the scalar 's'.

    Returns a new list with each element of the new list equal to the element
    at the same position in 'lst' divided by 's'.
    """
    return [l / float(s) for l in lst]


def divide_lists(lst_numer, lst_denom):
    """
    Divides each element of the nested list 'lst_numer' by 'lst_denom'.

    The division is done by taking each element of 'lst_numer' and for each
    index of that element, dividing the item at that index by the item at the
    same index of 'lst_denom'. See example below:

        >>> numer = [[1., 2.],
        ...          [3., 4.]]
        >>> denom = [0.5, 0.5]
        >>> divide_lists(numer, denom)
        [[2., 4.], [6., 8.]]

    NOTE: It is assumed that each element of 'lst_numer' has the same length
    as 'lst_denom' as shown in the dimensions of the arguments below.

    Arguments:
        lst_numer: nested list of list(dimensions N x M)
        lst_denom: list of denominators(dimensions 1 x M)

    Returns:
        A new list formed by dividing each element of 'lst_numer' by
        'lst_denom' according to the division process described above.
    """
    indexes = range(len(lst_denom))
    return [[n[i] / float(lst_denom[i]) for i in indexes] for n in lst_numer]


def normalize(points):
    """
    Normalizes a set of points on a per dimension basis.

    Each dimension is divided by its standard deviation accross all points.

    NOTE: If all the points are the same along any dimension, the resulting
    normalized value of all points along that dimension will be 0 because the
    standard deviation of a collection of equal values is 0 and we can't
    realistically divide by 0 so we instead set the normalized value to 0.

    Arguments:
        points: list of points
            Each row of the supplied list is a point and each column of those
            rows is a dimension of that point as shown below.

            #               d0  d1  d2
            >>> points = [[ 1., 2., 3.],  #  p0
            ...           [ 4., 5., 6.],  #  p1
            ...           [ 7., 8., 9.]]  #  p2

            Single dimension point list:
            #             d0
            >>> points = [1.,   #p0
            ...           2.,   #p1
            ...           3.,   #p2
            ...           4.]   #p3

            Equal points list:
            >>> points = [1., 1., 1.]
            [0., 0., 0.]

    Returns:
        The values in 'points' scaled by the standard deviation along each
        dimension.
    """
    # Check for a single dimension list. This check assumes that if the first
    # element is not a list then all elements are non-list and the list is
    # single dimension. If the list is single dimension just divide all the
    # points by the standard deviation and return that as the normalized list.
    if len(points) > 0 and not is_iterable(points[0]):
        std = std_dev(points)
        if std == 0:
            return [0] * len(points)
        else:
            return divide_by_scalar(points, std_dev(points))

    # Organize the points list as a list where each row is a list of values of
    # the same dimension.
    dimensions = zip(*points)

    # Compute the standard deviation of each dimension.
    std = [std_dev(d) for d in dimensions]

    # Divide all the point dimensions by the standard deviation of that
    # dimension over all points.
    if 0 in std:
        norm_points = []
        for point in points:
            norm_point = []
            for p, s in zip(point, std):
                if s == 0:
                    norm_point.append(0.0)
                else:
                    norm_point.append(p / s)

            norm_points.append(norm_point)

        return norm_points
    else:
        return divide_lists(points, std)


def is_nested(points):
    """
    Returns True if points is a nested iterable and False if not.

    A nested iterable is an iterable that is made of iterable elements. See
    the example below:

        >>> p = [[1, 2, 3],
        ...      [4, 5, 6]]
        >>> is_nested(p)
        True
        >>> p = [10, 20, 30]
        >>> is_nested(p)
        False
        >>> p = [[10], [20], [30]]
        >>> is_nested(p)
        True

    NOTE: This method only checks the first element of the iterable 'points'
    to make the determination of "nestedness". It is assumed that all elements
    of 'points' are either iterable or not iterable, that is, they match the
    property of the first element.

    """
    if is_iterable(points) and len(points) > 0:
        return is_iterable(points[0])

    return False


def get_dimension(points):
    """
    Returns the dimension of the 'points' list.

    The dimension is considered the number of dimensions(or columns) that make
    up the points in the list. For more details, see the examples below:

        >>> p = [[1, 2, 3],
        ...      [4, 5, 6]]
        >>> get_dimension(p)
        3
        >>> p = [10, 20, 30]
        >>> get_dimension(p)
        1

    This method checks that all points have the same dimension and will raise
    a ValueError if all the points do not share the same dimension.

    Arguments:
        points: list of points of any dimension

    Returns:
        The dimension of the point list(aka the number of columns) or raises a
        ValueError if the number of dimensions is not consistent over all
        points in 'points'.
    """

    if is_iterable(points[0]):
        dimension = len(points[0])
    else:
        dimension = 1

    i_dimension = -1
    for i in range(len(points)):
        if is_iterable(points[i]):
            i_dimension = len(points[i])
        else:
            i_dimension = 1

        if i_dimension != dimension:
            raise ValueError("Points must have the same number of dimensions.")

    return dimension


def sqr_euclidean_dist(point1, point2):
    """
    Calculates the square Euclidean distance between all dimension of 2 points.

    The returned value is a list of distances representing the squared
    Euclidean distance along each dimension of the two points. This is shown
    in the example below:

        >>> p1 = [1, 2, 3]
        >>> p2 = [3, 6, 9]
        >>> sqr_euclidean_dist(p1, p2)
        [4, 14, 36]

        >>> o1 = 5.4
        >>> o2 = 2.4
        >>> sqr_euclidean_dist(p1, p2)
        9.000000000000004

    NOTE: This method assumes 'point1' and 'point2' are both numbers or lists
    of equal length. No verification is done to make sure that both have the
    same type or that the list lengths are equal.

    Arguments:
        point1, point2: number or list of numbers

    Returns:
        The square Euclidean distance along each dimensions of the points.
    """
    if is_iterable(point1):
        return [(p1 - p2) ** 2 for p1, p2 in zip(point1, point2)]

    return (point1 - point2) ** 2


def index_of_min(values):
    """
    Finds and returns the index of the smallest item in the 'values' list.

    If multiple values are all equal to the minimum value then the one with
    the smallest index is returned.
    """
    min_value = float('Inf')
    min_index = 0

    for i in range(len(values)):
        if values[i] < min_value:
            min_value = values[i]
            min_index = i

    return min_index


def compute_clusters(points, centroids):
    """
    Computes cluster assignment and distance to cluster centroid for 'points'.

    Runs a vector quantization algorithm on the points using 'centroids' as
    the training set. This method can be considered the encoder part of the
    vector quantization algorithm where the codebook that is generated contains
    the cluster(centroid index) that each point belongs to and the distance
    between each point and its cluster centroid. The distance referred to
    above is the Euclidean distance.

    For some general info on vector quantization theory see:
        http://www.oocities.org/stefangachter/VectorQuantization/chapter_1.htm
        http://www.data-compression.com/vq.html

    Returns:
        clusters: A list such that clusters[i] is the index of the centroid
                  of the cluster that the ith point is a member of. This list
                  will have the same length as 'points'.
        distances: A list such that distances[i] represents the Euclidean
                   distance between the ith point and the centroid of the
                   cluster it is a member of. This list will have the same
                   length as 'points'.
    """
    if len(points) < 1:
        raise ValueError("cluster requires at least one point.")
    if len(centroids) < 1:
        raise ValueError("cluster requires at least one centroid.")

    d = get_dimension(points)
    n = len(points)
    cluster_indexes = range(len(centroids))

    if d != get_dimension(centroids):
        raise ValueError('Points and centroids must have the same '
                         'dimension(found {0} and {1} respectively)'.format(
                             d, get_dimension(centroids)))

    clusters = [0] * n
    min_distances = [0] * n
    for i in range(n):
        # Compute the squared Euclidean distance between this point and each
        # of the centroids.
        distances = [sqr_euclidean_dist(points[i], centroids[j])
                     for j in cluster_indexes]

        # Sum across all dimensions of each distance measure. If we only have
        # one dimension then this is simply the distance list itself.
        if d == 1 and not is_nested(centroids):
            distance_totals = distances
        else:
            distance_totals = \
                [sum(distances[j]) for j in range(len(distances))]

        # Find the index containing the minimum distance.
        clusters[i] = index_of_min(distance_totals)

        min_distances[i] = distance_totals[clusters[i]]

    # Do the square root now to get the Euclidean distance. We don't do this
    # in the loop so that we can save time by not taking the square root of
    # non-minimal distances.
    return clusters, [math.sqrt(dist) for dist in min_distances]


def dimension_mean(points):
    """
    Calculates the mean of the points along each dimension.

    If the points are of a single dimension, 'points' will just be a list of
    numbers and the mean of the list itself will be returned. For more
    details, see the example below:

        >>> p = [[1.0, 0.0],
        ...      [0.5, 2.0]]
        >>> dimension_mean(p)
        [0.75, 1.0]

        >>> p = [1., 3., 5., 10.]
        >>> dimension_mean(p)
        4.75
    """
    if get_dimension(points) == 1 and not is_nested(points):
        return sum(points) / float(len(points))

    # Organize the points list as a list where each row is a list of values
    # of the same dimension.
    dimensions = zip(*points)

    return [sum(d) / float(len(d)) for d in dimensions]


def kmeans(points, k_or_centroids, threshold=1e-5):
    """
    Runs the k-means algorithm on the points for k clusters.

    This method runs the k-means clustering algorithm assigning the 'points'
    to k clusters. k is determined in one of two ways depending on what is
    provided in 'k_or_centroids'. If 'k_or_centroids' is a list, then the
    contents are used as the centroids and k is the length of that list. If
    'k_or_centroids' is not a list of centroids it is assumed to be an integer
    to be used as k and the initial centroids are then k random points chosen
    from 'points'.

    See:
        computer_clusters()

    Returns:
        centroids: list of centroids of the clusters found during execution
        distance: the average mean distance between all points and the
                  centroid of the cluster they are a member of
    """
    # TODO: Add support for iterations if k is supplied and ignore iterations
    # if initial centroids are provided.
    if len(points) < 1:
        raise ValueError("points must contain at least 1 point.")

    if is_iterable(k_or_centroids):
        k = len(k_or_centroids)
        initial_centroids = k_or_centroids
    else:
        k = k_or_centroids
        initial_centroids = [p for p in random.sample(points, k)]

    if k < 1:
        raise ValueError("k must be >= 1.")

    centroids = list(initial_centroids)
    mean_difference = float('Inf')
    previous_mean_distance = None
    while mean_difference > threshold:
        num_centroids = len(centroids)

        # Determine cluster membership and distances for all points given the
        # current centroids.
        centroid_indexes, distances = compute_clusters(points, centroids)

        # Compute the mean distance of all points to their corresponding
        # cluster centroid.
        mean_distance = sum(distances) / float(len(distances))

        # Compute the difference in mean distance between this clustering step
        # and the last one.
        if previous_mean_distance is not None:
            mean_difference = previous_mean_distance - mean_distance

        # The following is the update step of the k-means algorithm where the
        # centroid position changes based on the points in each cluster. We
        # can safely ignore this step if the have reached the threshold for
        # minimum difference in mean distance.
        if mean_difference > threshold:
            for i in range(num_centroids):
                # Get all the points that are currently members of this
                # centroid's cluster.
                members = \
                    [p for c, p in zip(centroid_indexes, points) if c == i]

                # If the cluster has any points in it then update the centroid
                # of that cluster to be a point represented by the mean of all
                # points in that cluster along each dimension.
                if len(members) > 0:
                    centroids[i] = dimension_mean(members)
                else:
                    centroids[i] = None

            # Remove centroids of empty clusters.
            centroids = \
                [centroids[i] for i in range(len(centroids)) if centroids[i]]

        # Store this mean distance so we can access it in the next loop and
        # diff against this iterations mean distance.
        previous_mean_distance = mean_distance

    return centroids, previous_mean_distance


def find_outliers(points, outlier_threshold=3, normalized=True):
    """
    Finds and returns outliers in the 'points'.

    Outliers are those items in the 'points' that have a normalized distance
    that is at least 'outlier_threshold' away from the the calculated center
    of the population defined in 'points'. The normalized distance of a
    point is the distance from the point to its cluster's centroid divided by
    the mean distance of all point-to-centroid distances.

    Arguments:
        points: list of n-dimensional points
            An NxM list of lists defining the population to check for outliers
            where M is the number of dimensions per point and N is the number
            of points.
        outlier_threshold: float
            Used to define outliers. Outliers are points with normalized
            distances greater than this threshold.
        normalized: bool
            Value indicating whether 'points' have already been normalized or
            not. Passing False for this argument will result in the original
            'points' being normalized before the outlier search starts.

    Returns:
        The indexes of the outliers in 'points'.
    """
    if not normalized:
        points = normalize(points)

    d = get_dimension(points)

    # Organize the points list as a list where each row is a list of values of
    # the same dimension.
    if is_nested(points):
        dimensions = zip(*points)

    # Compute the mid-point index and construct the centroid by taking the
    # midpoint of the sorted list in each dimension.
    midpoint_index = (len(points) - 1) / 2

    if d == 1 and not is_nested(points):
        centroids = [sorted(points)[midpoint_index]]
    else:
        centroids = [[sorted(dim)[midpoint_index] for dim in dimensions]]

    # Calculate the distance from every point to the centroid.
    _, distances = compute_clusters(points, kmeans(points, centroids)[0])

    mean_distance = sum(distances) / float(len(distances))

    return [i for i, distance in enumerate(distances)
            if (mean_distance > 0 and
                (distance / mean_distance) >= outlier_threshold)]


def kmeans_optm(points, k=None, outlier_threshold=3):
    """
    Execute k-means clustering(for finding centroid) on, compute the clusters
    for, and run outlier detection on the 'points' population.

    Returns a dictionary containing the following data:
        'centroids': The k centers of the k clusters found by running the
                     k-means algorithm.
        'indexes':   An ordered list mapping each point in 'points' to the
                     centroid of the cluster it falls in.
        'distances': A list of distances between each point and the centroid
                     of its cluster.
        'outliers':  A list of outlier indexes in the 'points' list. This is
                     only returned if an 'outlier_threshold' is specified. If
                     outliers aren't required, set outlier_threshold=None.

    If 'k' is not supplied it will be calculated given the following formula:

        k = sqrt(n / 2)

    where n is the length of the 'points' list. The initialization method is
    optimized to find the mid-points of each cluster from a sorted list of
    points. This ultimately reduces the number of iterations required during
    clustering due to increased likelihood of convergence.

    Referenes:
        Number of clusters - http://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set#Rule_of_thumb # noqa
        Improved k-means initial centroids - http://www.ijcsit.com/docs/vol1issue2/ijcsit2010010214.pdf # noqa

    See:
        find_outliers()

    Arguments:
        points: list of n-dimensional points
        k: int or None
            The number of clusters to calculate. If 'k' is not supplied, it
            will be calculated according to the formula descibed above.
        outlier_threshold: float
            Used to define outliers. Outliers are points with normalized
            distances greater than this threshold.
    Returns:
        A dictionary containing the centroids, indexes of each point's
        centroid, distances from each point to its centroid and optionally a
        list of indexes of the outliers in 'points'. More detailed info on
        the return values are included above.
    """
    # If an outlier threshold is defined, remove outliers relative to the
    # population before running k-means clustering.
    if outlier_threshold:
        outliers = find_outliers(points, outlier_threshold, False)
        points = [p for i, p in enumerate(points) if i not in outliers]
    else:
        outliers = []

    d = get_dimension(points)
    n = len(points)

    # Compute the number of clusters if it wasn't specified.
    k = k or int(math.sqrt(n / 2))

    # Manually calculate the standard deviation for each dimension of the
    # point list in order to de-normalize the centroids later. Otherwise, the
    # centroid would be relative to the normalized dimensions rather than the
    # original.
    if d == 1 and not is_nested(points):
        std = std_dev(points)
    else:
        # Organize the points list as a list where each row is a list of
        # valuesof the same dimension.
        dimensions = zip(*points)
        std = [std_dev(dim) for dim in dimensions]

    norm_points = normalize(points)

    if d == 1 and not is_nested(points):
        sorted_points = sorted(norm_points)
    else:
        # Organize the normalized list as a list where each row is a list of
        # values of the same dimension.
        norm_dimensions = zip(*norm_points)

        # Sort the points by dimension and then return the dimension based
        # list back to the original point form so the sorted list has n
        # records and m dimensions just like the original points list.
        sorted_dimensions = [sorted(dim) for dim in norm_dimensions]
        sorted_points = [list(dim) for dim in zip(*sorted_dimensions)]

    step = n / k
    offset = step / 2
    initial_centroids = sorted_points[offset::step]

    # Perform the clustering then calculate the centroid each point is
    # associated with and the distance between each point and its centroid.
    # Centroids returned here are based on the normalized(see normalize())
    # points.
    centroids, _ = kmeans(norm_points, initial_centroids)
    indexes, distances = compute_clusters(norm_points, centroids)

    # Denormalize the centroids for downstream use. Do this by multiplying
    # each dimension of each centroid by the standard deviation along that
    # dimension that we calculated earlier.
    if d == 1 and not is_nested(points):
        denorm_centroids = [c * std for c in centroids]
    else:
        denorm_centroids = \
            [[dim * s for dim, s in zip(c, std)] for c in centroids]

    return {
        'centroids': denorm_centroids,
        'indexes': indexes,
        'distances': distances,
        'outliers': outliers,
    }


def weighted_counts(points, counts, k):
    """
    Calculate and return the weighted count of each centroid.

    Performs k-means clustering in order to identify the centroids and the
    distances between all points and their centroids. Weights and distances
    for the centroids are then constructed from all the points in that
    centroids cluster. Using those values, the weighted count is computed for
    each of the centroids and returned along with the centroid themselves. The
    points returned are a list of point objects where each point in the list
    has a list of 'values' representing the centroid coordinates and a 'count'
    which is the weighted count as computed for that centroid. Also returned
    is the list of outlier indexes in the 'points' list as determined by the
    k-means algorithm.

    Arguments:
        points - list of n-dimensional points to run k-means on.
        counts - the count for each point in the 'points' list. This list
                 must be of the same length as the 'points' list because the
                 count for a point is determined by accessing both 'points'
                 and 'counts' with the same index.
        k - the number of clusters(k-value) to send to the k-means algorithm.

    Returns:
        centroid_counts - A list of points where each point has 'values' list
        containing the coordinates of the centroid it is associated with and a
        'count' which is an integer representing the weighted count as
        computed for that centroid.
        outliers - A list of indexes of the outliers in 'point's as returned
        by the k-means algorithm.
    """
    result = kmeans_optm(points, k=k)
    outliers = [points[i] for i in result['outliers']]

    dist_weights = defaultdict(lambda: {'dist': [], 'count': []})
    for i, idx in enumerate(result['indexes']):
        dist_weights[idx]['dist'].append(result['distances'][i])
        dist_weights[idx]['count'].append(counts[i])

    centroid_counts = []

    # Determine best count relative to each point in the cluster
    for i, centroid in enumerate(result['centroids']):
        dist_sum = sum(dist_weights[i]['dist'])
        weighted_counts = []
        for j, dist in enumerate(dist_weights[i]['dist']):
            if dist_sum:
                wc = (1 - dist / dist_sum) * dist_weights[i]['count'][j]
            else:
                wc = dist_weights[i]['count'][j]
            weighted_counts.append(wc)

        if is_iterable(centroid):
            values = list(centroid)
        else:
            values = centroid

        centroid_counts.append({
            'values': values,
            'count': int(sum(weighted_counts)),
        })

    return centroid_counts, outliers

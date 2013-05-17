import math
from random import random
from collections import namedtuple

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

def std_dev(values):
    """
    Computes the standard deviation of the 'values' list. 

    TODO: Consider adding support for axes as in numpy:
        http://docs.scipy.org/doc/numpy/reference/generated/numpy.std.html
    
    Arguments:
        values: list
            A list of numbers to compute the standard deviation of.

    Returns:
        The standard deviation of the elements in the 'values' list.
    """
    # Compute the mean
    mean = sum(values, 0.0) / len(values)

    # Compute the square difference of all the values
    square_differences = [(v - mean)**2 for v in values]

    return math.sqrt(sum(square_differences) / len(square_differences))

def whiten(points):
    """
    Normalizes a set of points on a per dimension basis.

    Each dimension is divided by its standard deviation accross all points.

    Arguments:
        points: list of points
            Each row of the supplied list is a point and each column of those
            rows is a dimension of that point as shown below.

            #           d0  d1  d2
            points = [[ 1., 2., 3.],  #  p0
                      [ 4., 5., 6.],  #  p1
                      [ 7., 8., 9.]]  #  p2
            
            Single dimension point list:
            #         d0
            points = [1.,   #p0
                      2.,   #p1
                      3.,   #p2
                      4.]   #p3

    Returns:
        The values in 'points' scaled by the standard deviation along each
        dimension.
    """
    # Check for a single dimension list. This check assumes that if the first 
    # element is not a list then all elements are non-list and the list is 
    # single dimension. If the list is single dimension just divide all the 
    # points by the standard deviation and return that as the whitened list.
    if len(points) > 0 and not isinstance(points[0], list):
        standard_deviation = std_dev(points)
        return [p / standard_deviation for p in points]

    # Organize the points list as a list where each row is a list of values
    # of the same dimension
    dimensions = zip(*points)

    # Compute the standard deviation of each dimension
    std_devs = [std_dev(d) for d in dimensions]
    
    # Store index of each dimension to avoid recomputing in the loop below
    dimension_indeces = range(len(dimensions))

    # Divide all the point dimensions by the corresponding dimension standard
    # deviation.
    return [[p[i] / std_devs[i] for i in dimension_indeces] for p in points]

def sqr_euclidean(p1, p2):
    """
    Computes the squared Euclidean distance between 'p1' and 'p2'.
    """
    return sum([(p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)])

def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)

def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while True:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = sqr_euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, sqr_euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

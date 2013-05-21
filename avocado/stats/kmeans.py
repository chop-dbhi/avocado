import math
from random import random

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

def get_dimension(observations):
    """
    Returns the dimension of the observations list.

    The dimension is considered the number of columns or features that make
    up the observations. For example, the following observation list would
    have dimension 3.

        obs = [[1., 2., 3.],
               [4., 5., 6.]]

    This method checks that all observations have the same dimension and will
    raise a ValueError if all the observations do not share the same dimension.

    Arguments:
        observations: list of observations of any dimension

    Returns:
        The dimension of the observations list(aka the number of columns) or
        raises a ValueError if the number of dimensions is not consistent
        over all observations.
    """

    if isinstance(observations[0], list):
        dimension = len(observations[0])
    else:
        dimension = 1

    i_dimension = -1
    for i in range(len(observations)):
        if isinstance(observations[i], list):
            i_dimension = len(observations[i])
        else:
            i_dimension = 1
        
        if i_dimension != dimension:
            raise ValueError("Observations do not have a consistent dimension.")

    return dimension
    
def observation_sqr_euclidean(obs1, obs2):
    """
    Calculates the square Euclidean distance for each feature.

    The returned value is a list of distances representing the squared
    Euclidean distance along each feature of the observations. This is shown
    in the example below:

        o1 = [1, 2, 3]
        o2 = [3, 6, 9]
        observation_sqr_euclidean(o1, o2)

        #   [4, 14, 36]
    
    Returns:
        The square Euclidean distance along each feature of supplied 
        observations.
    """
    return [(o1 - o2) ** 2 for o1, o2 in zip(obs1, obs2)]

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

def vq(observations, codebook):
    """
    Vector quantization algorithm.

    Computes the Euclidean distance between each observation and each entry in 
    the code book. See below links for general VQ description:

    http://www.oocities.org/stefangachter/VectorQuantization/chapter_1.htm
    http://www.data-compression.com/vq.html

    Returns:
        encodings: A list of encodings such that encodings[i] is the encoding
                   of the ith observation.
        distances: A list of distances such that distances[i] represents the 
                   minimum distance between the ith observation and its
                   encoding.
    """
    
    if len(observations) < 1:
        raise ValueError("vq requires at least one observation. 0 observations found.")
    if len(codebook) < 1:
        raise ValueError("vq requires at least one codebook vector. 0 codebook entries found.")
    # Create copies of the observations and codebook just in case we need to 
    # transform to multi-dimensional.
    obs = list(observations)
    cb = list(codebook)

    # Since this method is meant to remove the dependency on scipy and scipy 
    # has no support for 1d arrays, we modify 1d lists to multi-dimensional 
    # lists in order to reuse the same multi-dimensional VQ algorithm and then 
    # simply flatten the result later in the case of 1d lists.
    # TODO: Write a Scalar Quantization method or make this 1d compatible
    #       without this hack.
    d = get_dimension(obs)
    if d == 1:
        obs = [[o] for o in observations]
        cb = [[c] for c in codebook]

    n = len(obs)

    if d != get_dimension(cb):
        raise ValueError("observations and codebook must have the same number of features(columns) per observation")

    encodings = [0] * n
    min_distances = [0] * n
    for i in range(n):
        # Compute the squared Euclidean distance between this observation and
        # every entry in the code book.
        distances = [observation_sqr_euclidean(obs[i], cb[j]) for j in range(len(cb))]
        
        # Sum across all dimensions of each distance measure.
        distance_totals = [sum(distances[j]) for j in range(len(distances))]

        # Find the index containing the minimum distance. This provides a 
        # decoding from the codevector to the output vector.
        encodings[i] = index_of_min(distance_totals)

        # Save the minimum distance to the output vector for the given 
        # codevector from the codebook and the encoding index.
        min_distances[i] = distance_totals[encodings[i]]
        
    # Do the square root now to get the Euclidean distance. We don't do this
    # in the loop so that we can save time by not taking the square root of 
    # non-minimal distances.
    return encodings, [math.sqrt(d) for d in min_distances]

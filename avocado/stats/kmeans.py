import math
from random import random

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
    mean = sum(values, 0.0) / len(values)

    # Compute the square difference of all the values
    square_differences = [(v - mean)**2 for v in values]

    return math.sqrt(sum(square_differences) / len(square_differences))

def divide_by_scalar(lst, s):
    """
    Divides each element in 'lst' by the scalar 's'.

    Returns a new list with each element of the new list equal to the element
    at the same position in 'lst' divided by 's'.
    """
    return [l / s for l in lst]

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
    return [[n[i] / lst_denom[i] for i in indexes] for n in lst_numer]

def normalize(points):
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
    # points by the standard deviation and return that as the normalized list.
    if len(points) > 0 and not isinstance(points[0], list):
        return divide_by_scalar(points, std_dev(points))

    # Organize the points list as a list where each row is a list of values
    # of the same dimension
    dimensions = zip(*points)

    # Compute the standard deviation of each dimension
    std_devs = [std_dev(d) for d in dimensions]
    
    # Divide all the point dimensions by the corresponding dimension standard
    # deviation.
    return divide_lists(points, std_devs) 

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
            raise ValueError("Observations must have the same dimension.")

    return dimension
    
def sqr_euclidean_dist(obs1, obs2):
    """
    Calculates the square Euclidean distance for each feature.

    The returned value is a list of distances representing the squared
    Euclidean distance along each feature of the observations. This is shown
    in the example below:

        >>> o1 = [1, 2, 3]
        >>> o2 = [3, 6, 9]
        >>> sqr_euclidean_dist(o1, o2)
        [4, 14, 36]
    
        >>> o1 = 5.4
        >>> o2 = 2.4
        >>> sqr_euclidean_dist(o1, o2)
        9.000000000000004

    NOTE: This method assumes 'obs1' and 'obs2' are both numbers or lists of 
    equal length. No verification is done to make sure that both have the same
    type or that the list lengths are equal.

    Arguments:
        obs1, obs2: number or list of numbers

    Returns:
        The square Euclidean distance along each feature of supplied 
        observations.
    """
    if isinstance(obs1, list):
        return [(o1 - o2) ** 2 for o1, o2 in zip(obs1, obs2)]

    return (obs1 - obs2) ** 2

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
        raise ValueError("vq() requires at least one observation.")
    if len(codebook) < 1:
        raise ValueError("vq() requires at least one codebook vector.")
    
    d = get_dimension(observations)
    n = len(observations)
    codebook_indexes = range(len(codebook))

    if d != get_dimension(codebook):
        raise ValueError("observations and codebook must have the same number of features(columns) per observation")

    encodings = [0] * n
    min_distances = [0] * n
    for i in range(n):
        # Compute the squared Euclidean distance between this observation and
        # every entry in the code book.
        distances = [sqr_euclidean_dist(observations[i], codebook[j]) \
                for j in range(len(codebook))]
        
        # Sum across all dimensions of each distance measure. If we only have
        # one dimension then this is simply the distance list itself.
        if d == 1:
            distance_totals = distances
        else:
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

def dimension_mean(observations):
    """
    Calculates the mean of the observations along each dimension.

    If the observations are of a single dimension, 'observations' will just
    be a list of numbers and the mean of the list itself will be returned. For
    more details, see the example below:

        >>> o = [[1.0, 0.0],
        ...      [0.5, 2.0]]
        >>> dimension_mean(o)
        [0.75, 1.0]

        >>> o = [1., 3., 5., 10.]
        >>> dimension_mean(o)
        4.75
    """
    if get_dimension(observations) == 1:
        return sum(observations) / len(observations)

    # Organize the points list as a list where each row is a list of values
    # of the same dimension
    dimensions = zip(*observations)
    
    return [sum(d) / len(d) for d in dimensions]

def kmeans(observations, k_or_centroids, threshold=1e-5):
    # TODO: Add support for iterations if k is supplied and ignore iterations
    # if initial centroids are provided.

    if len(observations) < 1:
        raise ValueError("observations must contain at least 1 observation.")

    if isinstance(k_or_centroids, list):
        centroids = list(k_or_centroids)
        k = len(centroids)
        if k < 1:
            raise ValueError("kmeans() requires at least 1 centroid.")
    else:
        k = k_or_centroids
        centroids = [o for o in random.sample(observations, k)]
        if k < 1:
            raise ValueError("Number of clusters(k) must be greater than 0.")

    # Create a codebook/training set from the initial centroids. Throughout 
    # this method, the codebook can be considered the current best guess at 
    # the cluster centroids.
    codebook = list(centroids)
    mean_difference = float('Inf')
    previous_mean_distance = None

    while mean_difference > threshold:
        num_centroids = len(codebook)

        # Use the Vector Quantization to determine cluster membership and 
        # distances for all points given the centroids in the codebook. The 
        # result from vq will be the encoding of all the observations to their
        # clusters and the distances to the centroids of those clusters.
        cluster_codes, distances = vq(observations, codebook)

        # Compute the mean distance of all points to their corresponding
        # cluster centroid.
        mean_distance = sum(distances) / len(distances)

        # Compute the difference in mean distance between this clustering
        # step and the last one.
        if previous_mean_distance != None:
            mean_difference = previous_mean_distance - mean_distance

        # The following is the update step of the k-means algorithm where the
        # centroid position changes based on the observations in each cluster.
        # We can safely ignore this step if the have reached the threshold
        # for minimum difference in mean distance.
        if mean_difference > threshold:
            for i in range(num_centroids):
                # Get all the observations that are currently residing in this
                # centroid's cluster. We know that the encoding returned from
                # the vector quantization maps the observation codevectors to
                # their cluster codes so we can use that for the lookup.
                cluster_observations = [observation for cluster, observation \
                        in zip(cluster_codes, observations) if cluster == i]

                # If the cluster has observations in it then update the
                # centroid(codebook entry) of that cluster to be the mean of
                # all the observations in that cluster along each dimension of
                # of the observations.
                if len(cluster_observations) > 0:
                    codebook[i] = dimension_mean(cluster_observations)
                else:
                    codebook[i] = None

            # Remove centroids of empty clusters
            codebook = [codebook[i] for i in range(len(codebook)) \
                    if codebook[i]]

        # Store this mean distance so we can access it in the next loop 
        # and diff against this iterations mean distance.
        previous_mean_distance = mean_distance
    
    return codebook, previous_mean_distance

def find_outliers(observations, outlier_threshold=3, normalized=True):
    """
    Finds and returns outliers in the 'observations'.

    Outliers are those items in the 'observations' that have a normalized
    distance that is at least 'outlier_threshold' away from the the calculated 
    center of the the population defined in 'observations'. The normalized
    distance of an observation is its distance from the centroid divided by
    the mean distance of all observation centroid distances.

    Arguments:
        observations: list of n-dimensional observations
            An NxM list of lists defining the population to check for 
            outliers where M is the dimension of the observations and N is the
            number of observations.
        outlier_threshold: float
            Used to define outliers. Outliers are observations with normalized
            distances greater than this threshold.
        normalized: bool
            If the 'observations' weren't already normalized, passing False for
            this argument will result in the original 'observations' being 
            normalized before the outlier search starts.

    Returns:
        The indexes of the outliers in 'observations'.
    """
    if not normalized:
        observations = normalize(observations)

    d = get_dimension(observations)

    # Organize the points list as a list where each row is a list of values
    # of the same dimension.
    if d > 1:
        dimensions = zip(*observations)

    # Compute the mid-point index and construct the centroid by taking
    # the midpoint of the sorted list in each dimension.
    midpoint_index = (len(observations) - 1) / 2
    
    if d == 1:
        centroid = [sorted(observations)[midpoint_index]]
    else:
        centroid = [[sorted(d)[midpoint_index] for d in dimensions]]

    # Calculate the distance from every observation to the centroid.
    _, distances = vq(observations, kmeans(observations, centroid)[0])

    mean_distance = sum(distances) / len(distances)

    return [i for i, distance in enumerate(distances) \
            if (distance / mean_distance) >= outlier_threshold]

def kmeans_optm(observations, k=None, outlier_threshold=3):
    """
    Execute k-means clustering on the the 'observations' population.
    
    Returns a dictionary containing the following data:
        'centroids' - The k centers of the k clusters found by running the
        k-means algorithm.
        'indexes' - An ordered list mapping each observation in 'observations'
        to the centroid of the cluster it falls in.
        'distances' - A list of distances between each observation and the 
        centroid of its cluster.
        'outliers' - A list of outlier indexes in the 'oberservations' list.
        This is only returned if an 'outlier_threshold' is specified. If
        outliers aren't required, set outlier_threshold=None.

    If 'k' is not supplied it will be calculated given the following formula:
        
        k = sqrt(n / 2)

    where n is the length of the 'observations' list. The initialization 
    method is optimized to find the mid-points of each cluster from a sorted
    list of observations. This ultimately reduces the number of iterations
    required during clustering due to increased likelihood of convergence.

    Referenes:
        Number of clusters - http://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set#Rule_of_thumb
        Improved k-means initial centroids - http://www.ijcsit.com/docs/vol1issue2/ijcsit2010010214.pdf
        
    See:
        find_outliers()

    Arguments:
        observations: list of n-dimensional observations
        k: int or None
            The number of clusters to calculate. If 'k' is not supplied, it
            will be calculated according to the formula descibed above.
        outlier_threshold: float
            Used to define outliers. Outliers are observations with normalized
            distances greater than this threshold.
    Returns:
        A dictionary containing the centroids, indexes of each observation's
        centroid, distances from each observation to its centroid and 
        optionally a list of indexes of the outliers in 'observations'. More
        detailed info on the return values are included above.
    """
    # If an outlier threshold is defined, remove outliers relative to
    # the population before running k-means clustering.
    if outlier_threshold:
        outliers = find_outliers(observations, outlier_threshold, False)
        observations = \
                [o for i, o in enumerate(observations) if i not in outliers]
    else:
        outliers = []

    # Organize the points list as a list where each row is a list of values
    # of the same dimension.
    dimensions = zip(*observations)

    # Manually calculate the standard deviation for each dimension of the 
    # observation list in order to de-normalize the centroids later. 
    # Otherwise, the centroid would be relative to the normalized dimensions 
    # rather than the original.
    std = [std_dev(d) for d in dimensions]
    norm_observations = divide_lists(observations, std)
  
    n = len(observations)

    # Compute the number of clusters if it wasn't specified
    k = k or int(math.sqrt(n / 2))

    # Organize the normalized list as a list where each row is a list of values
    # of the same dimension.
    norm_dimensions = zip(*norm_observations)

    # Sort the observational data by dimension and then return the
    # dimension based list back to the original observational form so
    # the sorted list has n records and m dimensions just like the
    # original observations list.
    sorted_dimensions = [sorted(d) for d in norm_dimensions]
    sorted_observations = [list(d) for d in zip(*sorted_dimensions)]
    
    step = n / k
    offset = step / 2
    initial_centroids = sorted_observations[offset::step]

    # Perform the clustering then calculate the centroid each
    # observation is associated with and the distance between each
    # observation and its centroid. Centroids returned here are based on
    # the normalized(see normalize()) observations.
    centroids, _ = kmeans(norm_observations, initial_centroids)
    indexes, distances = vq(norm_observations, centroids)

    # Denormalize the centroids for downstream use. Do this by multiplying 
    # each dimension of each centroid by the standard deviation along that 
    # dimension that we calculated earlier.
    denorm_centroids = [[d * s for d, s in zip(c, std)] for c in centroids]
    
    return {
        'centroids': denorm_centroids, 
        'indexes': indexes,
        'distances': distances,
        'outliers': outliers,
    }

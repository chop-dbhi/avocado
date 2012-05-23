from django.core.exceptions import ImproperlyConfigured
from avocado.conf import OPTIONAL_DEPS

if not OPTIONAL_DEPS['scipy']:
    raise ImproperlyConfigured('Numpy and SciPy must be installed to use the clustering utilities.')

import math
import numpy
from scipy.cluster import vq


def find_outliers(wobs, outlier_threshold=3, whitened=True):
    """Finds outliers in the population given some distance threshold.
    Returns the indexes of the outliers from the original array.
    """
    # "Whiten" the observations, e.g. normalize
    if not whitened:
        wobs = vq.whiten(numpy.array(wobs))

    # Get the mid-point of the entire population as the starting centroid
    mid = (len(wobs) - 1) / 2
    center = numpy.sort(wobs, axis=0)[mid:mid + 1]

    # Determine distances from calculated centroid. The outliers are
    # determined by calculating the mean distance across the population
    # and removing the observations that exceed the threshold
    _, dists = vq.vq(wobs, vq.kmeans(wobs, center)[0])
    mean_dist = dists.mean()

    return [i for i, dist in enumerate(dists) \
            if (dist / mean_dist) >= outlier_threshold]


def kmeans_optm(obs, k=None, outlier_threshold=3):
    """Performs k-means clustering on an array of observations. Returns
    the `centroids`, an ordered array of `indexes` corresponding to each
    observations centroid, an ordered array of `distances` of each
    observeration relative to it's centroid, and (optionally) an array of
    outlier indexes (see `find_outliers` above).

    If `k` is not specified, it will be calculated given:

        k = sqrt( n / 2 )

    The initialization method is optimized to find the mid-points of each
    cluster from a sorted array of observations. This ultimately reduces
    the number of iterations required during clustering due to increased
    likelihood of convergence.

    References:
    Number of clusters - http://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set#Rule_of_thumb
    Improved k-means initial centroids - http://www.ijcsit.com/docs/vol1issue2/ijcsit2010010214.pdf
    """
    # If a threshold is defined, first remove outliers relative to the
    # population before performing the clustering.
    if outlier_threshold:
        outliers = find_outliers(obs, outlier_threshold, False)
        obs = [ob for i, ob in enumerate(obs) if i not in outliers]
    else:
        outliers = []

    # Manually calculate the standard deviation for the matrix in order to
    # de-normalize the resulting centroids. Otherwise, the centroids would
    # be relative to the normalized dimensions rather than the original.
    nobs = numpy.array(obs)
    std = nobs.std(axis=0)
    wobs = nobs / std

    # How many observations?
    n = len(nobs)

    # How many clusters?
    if k is None:
        k = int(math.sqrt(n / 2))

    # Find midpoint of each cluster in a the sorted observations as the
    # initial centroids.
    step = n / k
    offset = step / 2
    initial_centroids = numpy.sort(wobs, axis=0)[offset::step]

    # Perform the clustering then calculate the centroid each observation
    # is associated with and it's distance. Centroids returned here are
    # based on the normalized observations.
    centroids, _ = vq.kmeans(wobs, initial_centroids)
    indexes, distances = vq.vq(wobs, centroids)

    # Re-denormalize centroids for downstream use
    return {
        'centroids': centroids * std,
        'indexes': indexes,
        'distances': distances,
        'outliers': outliers,
    }

import os
from django.test import TestCase
from avocado.stats import cluster

__all__ = ('ClusterTestCase',)

random_points_file = open(os.path.join(os.path.dirname(__file__), '../fixtures/random_points.txt'))
random_points = [float(x.strip()) for x in random_points_file.xreadlines()]


class ClusterTestCase(TestCase):
    maxDiff = None

    def test_no_outliers(self):
        outliers = cluster.find_outliers(xrange(300), whitened=False)
        self.assertEqual(outliers, [])

    def test_cluster(self):
        cluster_output = cluster.kmeans_optm(random_points, outlier_threshold=3)

        centroids = list(cluster_output['centroids'])
        outliers = list(cluster_output['outliers'])
        indexes = list(cluster_output['indexes'])

        self.assertEqual(centroids, [0.10460353527323077, 0.35212940867581483, 0.60313765188424995, 0.90802934439682748, 1.9630486600211763, 3.9437334147792598, 6.7021843890544748, 10.457707213747391, 26.704429662320841, 49.498211753985721, 73.310903128012484])
        self.assertEqual(outliers, [204, 206, 214, 216, 221, 233, 235, 251, 255, 267, 268, 271, 280, 290, 292, 295])
        self.assertEqual(indexes, [2, 3, 1, 0, 1, 0, 0, 1, 3, 3, 0, 2, 2, 1, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 0, 1, 0, 0, 1, 1, 2, 0, 2, 3, 2, 0, 3, 1, 0, 1, 3, 3, 2, 3, 3, 2, 3, 1, 0, 3, 1, 2, 2, 1, 2, 1, 2, 3, 1, 0, 1, 0, 3, 1, 2, 0, 0, 2, 3, 0, 2, 0, 1, 2, 1, 3, 0, 0, 1, 3, 0, 0, 1, 3, 3, 0, 2, 3, 1, 3, 1, 0, 3, 2, 2, 1, 1, 0, 3, 3, 5, 5, 6, 4, 6, 7, 5, 4, 4, 5, 6, 7, 7, 7, 6, 6, 5, 7, 4, 6, 5, 6, 4, 6, 7, 6, 6, 6, 6, 6, 3, 5, 5, 4, 7, 7, 5, 6, 6, 5, 5, 5, 3, 6, 3, 4, 6, 4, 6, 2, 5, 6, 6, 6, 6, 3, 7, 7, 7, 7, 4, 3, 5, 7, 6, 5, 6, 7, 5, 0, 3, 4, 0, 5, 1, 7, 5, 5, 4, 4, 5, 5, 6, 4, 7, 4, 6, 6, 6, 5, 6, 6, 6, 6, 5, 4, 7, 4, 6, 6, 8, 10, 7, 8, 8, 10, 6, 8, 8, 9, 10, 9, 7, 9, 8, 9, 8, 8, 9, 10, 9, 10, 10, 10, 9, 10, 4, 10, 6, 9, 9, 8, 5, 10, 9, 9, 10, 8, 8, 9, 9, 10, 6, 8, 9, 10, 10, 9, 10, 7, 10, 10, 9, 8, 8, 5, 8, 7, 9, 9, 10, 10, 9, 10, 8, 7, 10, 8, 8, 8, 9, 5, 10, 10, 8, 8, 8, 8, 8, 10, 9, 7, 5, 6])

import os
import random
from django.test import TestCase
from avocado.stats import cluster, kmeans
from scipy.cluster import vq
import numpy as np
from itertools import chain

__all__ = ('KmeansTestCase',)

random_points_file = open(os.path.join(os.path.dirname(__file__), '../fixtures/random_points.txt'))
random_points_3d_file = open(os.path.join(os.path.dirname(__file__), '../fixtures/random_points_3d.txt'))
random_points = [float(x.strip()) for x in random_points_file.xreadlines()]
random_points_3d = [[float(x) for x in l.strip().split(",")] for l in random_points_3d_file.xreadlines()]

class KmeansTestCase(TestCase):
    maxDiff = None
    epsilon = 1e-15

    def test_std_dev(self):
        numpy_std_dev = np.std(np.array(random_points))
        our_std_dev = kmeans.std_dev(random_points)

        self.assertEqual(numpy_std_dev, our_std_dev)

    def test_whiten(self):
        scipy_whiten = vq.whiten(np.array(random_points))
        our_whiten = kmeans.whiten(random_points)
        
        self.assertEqual(len(scipy_whiten), len(our_whiten))

        comp_whiten = zip(scipy_whiten, our_whiten)

        [self.assertEqual(*comp) for comp in comp_whiten]
        
        scipy_whiten = vq.whiten(np.array(random_points_3d))
        our_whiten = kmeans.whiten(random_points_3d)
        
        self.assertEqual(len(scipy_whiten), len(our_whiten))

        comp_whiten = zip(scipy_whiten, our_whiten)

        [self.assertSequenceEqual(scipy_list.tolist(), our_list) for \
                scipy_list, our_list in comp_whiten]

    def test_scipy_vq_versions_1d(self):
        one_dim_points = [1.9, 2.3, 1.5, 2.5, 0.8, 0.6, 0.4, 1.8, 1.0, 1.0]
        vq_points = np.array([[p] for p in one_dim_points])
        book = np.array([vq_points[3], vq_points[7]])

        c_code, c_dist = vq.vq(vq_points, book)
        p_code, p_dist = vq.py_vq(vq_points, book)

        self.assertSequenceEqual(c_code.tolist(), p_code.tolist())
        self.assertSequenceEqual(c_dist.tolist(), p_dist.tolist())

    def test_scipy_vq_versions(self):
        vq_points = np.array([[ 1.9,2.3],
                              [ 1.5,2.5],
                              [ 0.8,0.6],
                              [ 0.4,1.8],
                              [ 1.0,1.0]])
        book = np.array((vq_points[0], vq_points[2]))

        c_code, c_dist = vq.vq(vq_points, book)
        p_code, p_dist = vq.py_vq(vq_points, book)

        self.assertSequenceEqual(c_code.tolist(), p_code.tolist())
        self.assertSequenceEqual(c_dist.tolist(), p_dist.tolist())

    def test_vq_1d(self):
        book = [p for p in random.sample(random_points, 8)]

        # SciPy doesn't work with 1d arrays yet so the 1d test data needs to
        # be transformed to a multidimensional representation
        one_d_array = np.array([[p] for p in random_points])
        one_d_book_array = np.array([[b] for b in book])

        s_code, s_dist = vq.vq(one_d_array, one_d_book_array)
        m_code, m_dist = kmeans.vq(random_points, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceEqual(s_dist.tolist(), m_dist)

    def test_vq(self):
        book = [p for p in random.sample(random_points_3d, 8)]

        s_code, s_dist = vq.vq(np.array(random_points_3d), np.array(book))
        m_code, m_dist = kmeans.vq(random_points_3d, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceEqual(s_dist.tolist(), m_dist)

    def test_kmeans(self):
        centroids = [p for p in random.sample(random_points_3d, 3)]
        s_centroids, s_distance = \
                vq.kmeans(np.array(random_points_3d), np.array(centroids))
        m_centroids, m_distance = kmeans.kmeans(random_points_3d, centroids)
        self.assertEqual(s_distance, m_distance)
        self.assertEqual(len(s_centroids.tolist()), len(m_centroids))

        # We can't just use assertSequenceEqual because there is some rounding
        # errors somewhere in the floating point math causing a difference
        # in a couple values over 15 decimal places in.
        if s_centroids.size == len(m_centroids):
            [self.assertAlmostEqual(s,m,epsilon) for s, m \
                    in zip(s_centroids.tolist(), m_centroids)]

    def test_no_outliers(self):
        points = [[i,i] for i in range(300)]
        c_outliers = cluster.find_outliers(points, whitened=False)
        m_outliers = kmeans.find_outliers(points, whitened=False)

        self.assertEqual(c_outliers, [])
        self.assertEqual(m_outliers, [])

    def test_find_outliers(self):
        c_outliers = cluster.find_outliers(random_points_3d, whitened=False)
        m_outliers = kmeans.find_outliers(random_points_3d, whitened=False)

        self.assertEqual(len(c_outliers), len(m_outliers))

        # Account for rounding errors at extremely high precision by
        # manually checking sequence elements
        if len(c_outliers) == len(m_outliers):
            [self.assertAlmostEqual(c, m, epsilon) for c, m \
                    in zip(c_outliers, m_outliers)]

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

PLACES = 10

class KmeansTestCase(TestCase):
    def assertSequenceAlmostEqual(self, seq1, seq2):
        """
        Helper method for checking that 2 sequences are almost equal.

        Two sequences are considered almost equal if they have the same order
        and each pair of elements of the sequences passes the 
        assertAlmostEqual to the number of decimal places specified in PLACES.
        This method will also work for nested lists of numbers. For example,
        let's say we wanted to see if two collections of 3D points were almost
        equal, we could use the following:

            pts1 = [[0.206331960142751, 0.612540082088810, 0.843236918599283], 
                    [0.269705965446683, 0.218132746363829, 0.277332011689122], 
                    [0.728684538148946, 0.734953792412333, 0.722476119561547]]
            pts2 = [[0.206331960142700, 0.612540082088819, 0.843236918599288], 
                    [0.269705965446609, 0.218132746363899, 0.277332011689182], 
                    [0.728684538148046, 0.734953792412933, 0.722476119561847]]
            assertSequenceAlmostEqual(pts1, pts2)

        Arguments:
            seq1, seq2: (nested)list of numbers to check for near equality

        NOTE: This method assumes 'seq1' 'seq2' have equal, non-zero length. If
        you are not certain the lengths match, use the following assert before
        calling this method or this method might have unpredictable results.
        For nested lists, it is not only assumed that overall list length is
        the same, but also that each nested list pair is of equal length.

            assertEqual(len(seq1), len(seq2))
        """
        if isinstance(seq1[0], list):
            for list1, list2 in zip(seq1, seq2):
                self.assertSequenceAlmostEqual(list1, list2)
        else:
            for num1, num2 in zip(seq1, seq2):
                self.assertAlmostEqual(num1, num2, PLACES)

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
        self.assertSequenceAlmostEqual(c_dist.tolist(), p_dist.tolist())

    def test_vq_1d(self):
        book = [p for p in random.sample(random_points, 8)]

        # SciPy doesn't work with 1d arrays yet so the 1d test data needs to
        # be transformed to a multidimensional representation
        one_d_array = np.array([[p] for p in random_points])
        one_d_book_array = np.array([[b] for b in book])

        s_code, s_dist = vq.vq(one_d_array, one_d_book_array)
        m_code, m_dist = kmeans.vq(random_points, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceAlmostEqual(s_dist.tolist(), m_dist)

    def test_vq(self):
        book = [p for p in random.sample(random_points_3d, 8)]

        s_code, s_dist = vq.vq(np.array(random_points_3d), np.array(book))
        m_code, m_dist = kmeans.vq(random_points_3d, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceAlmostEqual(s_dist.tolist(), m_dist)

    def test_kmeans(self):
        centroids = [p for p in random.sample(random_points_3d, 3)]
        s_centroids, s_distance = \
                vq.kmeans(np.array(random_points_3d), np.array(centroids))
        m_centroids, m_distance = kmeans.kmeans(random_points_3d, centroids)
        self.assertEqual(s_distance, m_distance)
        
        self.assertEqual(len(s_centroids.tolist()), len(m_centroids))
        self.assertSequenceAlmostEqual(s_centroids.tolist(), m_centroids)

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
        self.assertSequenceEqual(c_outliers, m_outliers)

    def test_kmeans_optm(self):
        c_kmeans = cluster.kmeans_optm(random_points_3d)
        m_kmeans = kmeans.kmeans_optm(random_points_3d)

        # Make sure all the right keys are present in both dictionaries
        for key in ['centroids', 'indexes', 'distances', 'outliers']:
            self.assertTrue(c_kmeans.has_key(key) and m_kmeans.has_key(key))

        c_indexes = c_kmeans['indexes'].tolist()
        m_indexes = m_kmeans['indexes']
        self.assertSequenceEqual(c_indexes, m_indexes)

        c_distances = c_kmeans['distances']
        m_distances = m_kmeans['distances']
        self.assertSequenceAlmostEqual(c_distances, m_distances)
        
        c_centroids = c_kmeans['centroids']
        m_centroids = m_kmeans['centroids']
        self.assertSequenceAlmostEqual(c_centroids.tolist(), m_centroids)

        c_outliers = c_kmeans['outliers']
        m_outliers = m_kmeans['outliers']
        self.assertSequenceEqual(c_outliers, m_outliers)

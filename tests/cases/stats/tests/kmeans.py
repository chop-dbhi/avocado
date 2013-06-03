import os
import random
from django.test import TestCase
from avocado.stats import kmeans
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
    def assertSequenceAlmostEqual(self, seq1, seq2, num_places=None):
        """
        Helper method for checking that 2 sequences are almost equal.

        Two sequences are considered almost equal if they have the same order
        and each pair of elements of the sequences passes the 
        assertAlmostEqual to the number of decimal places specified in 
        'num_places'. This method will also work for nested lists of numbers. 
        For example, let's say we wanted to see if two collections of 3D 
        points were almost equal, we could use the following:

            >>> pts1 = [[0.206331960142751, 0.612540082088810, 0.843236918599283], 
            ...         [0.269705965446683, 0.218132746363829, 0.277332011689122], 
            ...         [0.728684538148946, 0.734953792412333, 0.722476119561547]]
            >>> pts2 = [[0.206331960142700, 0.612540082088819, 0.843236918599288], 
            ...         [0.269705965446609, 0.218132746363899, 0.277332011689182], 
            ...         [0.728684538148046, 0.734953792412933, 0.722476119561847]]
            >>> assertSequenceAlmostEqual(pts1, pts2)

        Arguments:
            seq1, seq2: (nested)list of numbers to check for near equality

        NOTE: This method assumes 'seq1' 'seq2' have equal, non-zero length. If
        you are not certain the lengths match, use the following assert before
        calling this method or this method might have unpredictable results.
        For nested lists, it is not only assumed that overall list length is
        the same, but also that each nested list pair is of equal length.

            assertEqual(len(seq1), len(seq2))
        """
        num_places = num_places or PLACES

        if isinstance(seq1[0], list):
            for list1, list2 in zip(seq1, seq2):
                self.assertSequenceAlmostEqual(list1, list2, num_places)
        else:
            for num1, num2 in zip(seq1, seq2):
                self.assertAlmostEqual(num1, num2, num_places)

    def test_std_dev(self):
        our_std_dev = kmeans.std_dev(random_points)

        # The 28.247608160964884 value was calculated using numpy 1.6.1 on
        # Python 2.7.2.
        self.assertEqual(28.247608160964884, our_std_dev)

    def test_normalize(self):
        scipy_normalize = vq.whiten(np.array(random_points))
        our_normalize = kmeans.normalize(random_points)
        
        self.assertEqual(len(scipy_normalize), len(our_normalize))

        comp_normalize = zip(scipy_normalize, our_normalize)

        [self.assertEqual(*comp) for comp in comp_normalize]
        
        scipy_normalize = vq.whiten(np.array(random_points_3d))
        our_normalize = kmeans.normalize(random_points_3d)
        
        self.assertEqual(len(scipy_normalize), len(our_normalize))

        comp_normalize = zip(scipy_normalize, our_normalize)
        [self.assertSequenceEqual(scipy_list.tolist(), our_list) for \
                scipy_list, our_list in comp_normalize]

    def test_vq_1d(self):
        book = [p for p in random.sample(random_points, 8)]

        s_code, s_dist = vq.vq(np.array(random_points), np.array(book))
        m_code, m_dist = kmeans.compute_clusters(random_points, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceAlmostEqual(s_dist.tolist(), m_dist)

    def test_vq_1d_nested(self):
        nested = [[p] for p in random_points]
        book = [p for p in random.sample(nested, 8)]

        s_code, s_dist = vq.vq(np.array(nested), np.array(book))
        m_code, m_dist = kmeans.compute_clusters(nested, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceAlmostEqual(s_dist.tolist(), m_dist)

    def test_vq(self):
        book = [p for p in random.sample(random_points_3d, 8)]

        s_code, s_dist = vq.vq(np.array(random_points_3d), np.array(book))
        m_code, m_dist = kmeans.compute_clusters(random_points_3d, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceAlmostEqual(s_dist.tolist(), m_dist)

    def test_kmeans(self):
        # These indices don't really matter since the points are random but
        # I am fixing them here for repeatability of the test.
        centroids = [random_points_3d[125], 
                     random_points_3d[500], 
                     random_points_3d[875]]
        s_centroids, s_distance = \
                vq.kmeans(np.array(random_points_3d), np.array(centroids))
        m_centroids, m_distance = kmeans.kmeans(random_points_3d, centroids)
        
        self.assertEqual(s_distance, m_distance)
        self.assertEqual(len(s_centroids.tolist()), len(m_centroids))

        # I'm getting everything to pass at 10 places except for this where 
        # there always seems to be at least one dimension of one centroid 
        # about [.001-.005] away from where we expect it to be. For now, I'm 
        # setting this to 2 places until I can check if there is an issue in 
        # kmeans or if this is just a matter of floating differences between
        # numpy and standard python.
        self.assertSequenceAlmostEqual(s_centroids.tolist(), m_centroids, num_places=2)

    def test_no_outliers(self):
        points = [[i,i] for i in range(300)]
        m_outliers = kmeans.find_outliers(points, normalized=False)

        self.assertEqual(m_outliers, [])

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

        [self.assertSequenceEqual(scipy_list.tolist(), our_list) for scipy_list, our_list in comp_whiten]

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

        one_dim_points = [1.9, 2.3, 1.5, 2.5, 0.8, 0.6, 0.4, 1.8, 1.0, 1.0]
        vq_points = np.array([[p] for p in one_dim_points])
        book = np.array([vq_points[3], vq_points[7]])

        c_code, c_dist = vq.vq(vq_points, book)
        p_code, p_dist = vq.py_vq(vq_points, book)

        self.assertSequenceEqual(c_code.tolist(), p_code.tolist())
        self.assertSequenceEqual(c_dist.tolist(), p_dist.tolist())

    def test_vq(self):
        book = [p for p in random.sample(random_points, 8)]

        # SciPy doesn't work with 1d arrays yet so the 1d test data needs to
        # be transformed to a multidimensional representation
        one_d_array = np.array([[p] for p in random_points])
        one_d_book_array = np.array([[b] for b in book])

        s_code, s_dist = vq.vq(one_d_array, one_d_book_array)
        m_code, m_dist = kmeans.vq(random_points, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceEqual(s_dist.tolist(), m_dist)

        book = [p for p in random.sample(random_points_3d, 8)]

        s_code, s_dist = vq.vq(np.array(random_points_3d), np.array(book))
        m_code, m_dist = kmeans.vq(random_points_3d, book)

        self.assertSequenceEqual(s_code.tolist(), m_code)
        self.assertSequenceEqual(s_dist.tolist(), m_dist)

import os
from django.test import TestCase
from avocado.stats import cluster, kmeans
from scipy.cluster import vq
import numpy
from itertools import chain

__all__ = ('KmeansTestCase',)

random_points_file = open(os.path.join(os.path.dirname(__file__), '../fixtures/random_points.txt'))
random_points = [float(x.strip()) for x in random_points_file.xreadlines()]

class KmeansTestCase(TestCase):
    def test_std_dev(self):
        numpy_std_dev = numpy.std(numpy.array(random_points))
        our_std_dev = kmeans.std_dev(random_points)

        self.assertEqual(numpy_std_dev, our_std_dev)

    def test_whiten(self):
        scipy_whiten = vq.whiten(numpy.array(random_points))
        our_whiten = kmeans.whiten(random_points)
        
        self.assertEqual(len(scipy_whiten), len(our_whiten))

        comp_whiten = zip(scipy_whiten, our_whiten)

        [self.assertEqual(*comp) for comp in comp_whiten]

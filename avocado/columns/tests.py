import unittest

from avocado.tests import models
from avocado.modeltree import ModelTree
from .models import ColumnConcept
from . import ColumnSet

__all__ = ('ColumnSetTestCase',)

class ColumnSetTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_column_ordering(self):
        mt = ModelTree(models.Root)
        concepts = ColumnConcept.objects.all()

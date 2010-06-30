from django.test import TestCase

from avocado.columns.models import ColumnConcept
from avocado.fields.utils import M, AmbiguousFieldName

__all__ = ('MTestCase',)

ORIG_MODEL_TREE = M.model_tree

class MTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def setUp(self):
        M.model_tree = ORIG_MODEL_TREE
    
    def test_error(self):
        M.model_tree = None
        self.assertRaises(RuntimeError, M, failing__test=4)
        
    def test_variations(self):
        concepts = ColumnConcept.objects.filter(M(filter_name='Simple'))
        self.assertEqual(len(concepts), 4)
        
        concepts = ColumnConcept.objects.filter(M(filter_name__icontains='Sim'))
        self.assertEqual(len(concepts), 4)
        
        concepts = ColumnConcept.objects.filter(M(avocado__fieldconcept__filter_name='Simple'))
        self.assertEqual(len(concepts), 4)
        
        concepts = ColumnConcept.objects.filter(M(avocado__fieldconcept__filter_name__icontains='Sim'))
        self.assertEqual(len(concepts), 4)
        
        M.model_tree = None
        
        concepts = ColumnConcept.objects.filter(M(ORIG_MODEL_TREE,
            filter_name='Simple'))
        self.assertEqual(len(concepts), 4)
        
        concepts = ColumnConcept.objects.filter(M(ORIG_MODEL_TREE,
            filter_name__icontains='Sim'))
        self.assertEqual(len(concepts), 4)
        
        concepts = ColumnConcept.objects.filter(M(ORIG_MODEL_TREE,
            avocado__fieldconcept__filter_name='Simple'))
        self.assertEqual(len(concepts), 4)
        
        concepts = ColumnConcept.objects.filter(M(ORIG_MODEL_TREE,
            avocado__fieldconcept__filter_name__icontains='Sim'))
        self.assertEqual(len(concepts), 4)

    def test_ambiguous(self):
        self.assertRaises(AmbiguousFieldName, M, name='Foo')
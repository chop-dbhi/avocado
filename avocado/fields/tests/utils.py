from django.test import TestCase

from avocado.columns.models import Column
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS
from avocado.fields.utils import M, AmbiguousField

__all__ = ('MTestCase',)

class MTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_variations(self):
        concepts = Column.objects.filter(M(field_name='keywords'))
        self.assertEqual(len(concepts), 1)

        concepts = Column.objects.filter(M(field_name__icontains='key'))
        self.assertEqual(len(concepts), 1)

        concepts = Column.objects.filter(M(avocado__field__field_name='keywords'))
        self.assertEqual(len(concepts), 1)

        concepts = Column.objects.filter(M(avocado__field__field_name__icontains='key'))
        self.assertEqual(len(concepts), 1)
        M.modeltree = None

        concepts = Column.objects.filter(M(DEFAULT_MODELTREE_ALIAS,
            field_name='keywords'))
        self.assertEqual(len(concepts), 1)

        concepts = Column.objects.filter(M(DEFAULT_MODELTREE_ALIAS,
            field_name__icontains='key'))
        self.assertEqual(len(concepts), 1)

        concepts = Column.objects.filter(M(DEFAULT_MODELTREE_ALIAS,
            avocado__field__field_name='keywords'))
        self.assertEqual(len(concepts), 1)

        concepts = Column.objects.filter(M(DEFAULT_MODELTREE_ALIAS,
            avocado__field__field_name__icontains='key'))
        self.assertEqual(len(concepts), 1)

    def test_ambiguous(self):
        self.assertRaises(AmbiguousField, M, name='Foo')

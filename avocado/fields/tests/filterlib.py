from django.test import TestCase
from django.db.models import Q

from avocado.modeltree import ModelTree
from avocado.exceptions import RegisterError
from avocado.columns.models import ColumnConcept
from avocado.fields.filterlib import FilterLibrary, SimpleFilter
from avocado.fields.cache import get_concept

__all__ = ('FilterLibraryTestCase',)

class FilterLibraryTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_no_filters(self):
        library = FilterLibrary()
        self.assertEqual(library._cache, {})

    def test_bad_register(self):
        library = FilterLibrary()

        library.register(SimpleFilter)

        class FooFilter(object):
            pass

        self.assertRaises(RegisterError, library.register, FooFilter)

    def test_simple_filter(self):
        sfilter = SimpleFilter()
        mt = ModelTree(ColumnConcept)
        fc1 = get_concept(1)

        self.assertEqual(str(sfilter(mt, fc1, 'exact', 'foo')), str(Q(name__exact=u'foo')))


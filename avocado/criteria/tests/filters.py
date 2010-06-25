from django.test import TestCase

from avocado.criteria.filters import (FilterLibrary, AlreadyRegisteredError,
    RegisterError, AbstractFilter)

__all__ = ('FilterLibraryTestCase',)

class FilterLibraryTestCase(TestCase):
    def test_no_filters(self):
        library = FilterLibrary()
        self.assertEqual(library._cache, {})

    def test_bad_register(self):
        library = FilterLibrary()

        @library.register
        class SimpleFilter(AbstractFilter):
            def filter(self, modeltree, fields, params):
                
                

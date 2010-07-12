from django.test import TestCase
from django.db.models import Q

from avocado.modeltree import ModelTree
from avocado.exceptions import RegisterError
from avocado.columns.models import ColumnConcept
from avocado.fields.translate import TranslatorLibrary, SimpleTranslator
from avocado.fields.cache import cache

__all__ = ('TranslatorLibraryTestCase',)

class TranslatorLibraryTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_no_filters(self):
        library = TranslatorLibrary()
        self.assertEqual(library._cache, {})

    def test_bad_register(self):
        library = TranslatorLibrary()

        library.register(SimpleTranslator)

        class FooTranslator(object):
            pass

        self.assertRaises(RegisterError, library.register, FooTranslator)

    def test_simple_filter(self):
        sfilter = SimpleTranslator()
        mt = ModelTree(ColumnConcept)
        fc1 = cache.get(1)

        self.assertEqual(str(sfilter(mt, fc1, 'exact', 'foo')), str(Q(name__exact=u'foo')))


from django.test import TestCase
from django.db.models import Q

from avocado.modeltree import DEFAULT_MODELTREE
from avocado.exceptions import RegisterError
from avocado.fields.translate import TranslatorLibrary, DefaultTranslator
from avocado.fields.cache import cache

__all__ = ('TranslatorLibraryTestCase',)

class TranslatorLibraryTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_no_translators(self):
        library = TranslatorLibrary()
        self.assertEqual(library._cache, {})

    def test_bad_register(self):
        library = TranslatorLibrary()

        library.register(DefaultTranslator)

        class FooTranslator(object):
            pass

        self.assertRaises(RegisterError, library.register, FooTranslator)

    def test_default(self):
        t = DefaultTranslator()
        c = cache.get(1)

        self.assertEqual(str(t(c, 'iexact', 'foo', DEFAULT_MODELTREE)), str(Q(name__iexact=u'foo')))


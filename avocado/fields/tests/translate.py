from django.test import TestCase
from django.db.models import Q

from avocado.modeltree import DEFAULT_MODELTREE
from avocado.exceptions import RegisterError
from avocado.fields.translate import library, DefaultTranslator
from avocado.fields.cache import cache

__all__ = ('TranslatorLibraryTestCase',)

class TranslatorLibraryTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_bad_register(self):
        class FooTranslator(object):
            pass

        self.assertRaises(RegisterError, library.register, FooTranslator)

    def test_default(self):
        t = DefaultTranslator()
        c = cache.get(1)

        q, a = t(DEFAULT_MODELTREE, c, 'iexact', 'foo')

        self.assertEqual(str(q), str(Q(name__iexact=u'foo')))


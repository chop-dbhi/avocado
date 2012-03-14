from django.test import TestCase
from django.db.models import Q

from avocado.exceptions import RegisterError
from avocado.fields.models import Field
from avocado.fields.translate import library, DefaultTranslator

__all__ = ('TranslatorLibraryTestCase',)

class TranslatorLibraryTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def test_bad_register(self):
        class FooTranslator(object):
            pass

        self.assertRaises(RegisterError, library.register, FooTranslator)

    def test_default(self):
        t = DefaultTranslator()
        c = Field.objects.get(pk=1)

        q, a = t(c, 'iexact', 'foo')

        self.assertEqual(str(q), str(Q(name__iexact=u'foo')))


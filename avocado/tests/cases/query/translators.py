from avocado.tests.base import BaseTestCase

__all__ = ('TranslatorTestCase',)

class TranslatorTestCase(BaseTestCase):
    def test(self):
        trans = self.is_manager.translate(value=False)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('is_manager__exact', False))")

        trans = self.salary.translate(value=50000)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__exact', 50000.0), ('title__id__isnull', False))")

        trans = self.first_name.translate(value='Robert')
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('first_name__exact', u'Robert'))")

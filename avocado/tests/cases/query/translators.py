from avocado.tests.base import BaseTestCase
from avocado.models import DataField


class TranslatorTestCase(BaseTestCase):
    def setUp(self):
        super(TranslatorTestCase, self).setUp()
        self.is_manager = DataField.objects.get_by_natural_key('tests', 'employee', 'is_manager')
        self.salary = DataField.objects.get_by_natural_key('tests', 'title', 'salary')
        self.first_name = DataField.objects.get_by_natural_key('tests', 'employee', 'first_name')

    def test(self):
        trans = self.is_manager.translate(value=False)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('is_manager__exact', False))")

        trans = self.salary.translate(value=50000)
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('title__salary__exact', 50000.0), ('title__id__isnull', False))")

        trans = self.first_name.translate(value='Robert')
        self.assertEqual(str(trans['query_modifiers']['condition']), "(AND: ('first_name__exact', u'Robert'))")

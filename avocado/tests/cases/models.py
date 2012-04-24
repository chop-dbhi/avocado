from django.core.cache import cache
from django.core import management
from avocado.tests.base import BaseTestCase
from avocado.models import DataField, DataCategory, DataConcept


class ModelInstanceCacheTestCase(BaseTestCase):
    def test_datafield_cache(self):
        cache.clear()

        pk = self.is_manager.pk
        # New query, object is fetched from cache
        queryset = DataField.objects.filter(pk=pk)
        self.assertEqual(queryset._result_cache, None)

        self.is_manager.save()

        queryset = DataField.objects.filter(pk=pk)
        self.assertEqual(queryset._result_cache[0].pk, pk)


class DataFieldTestCase(BaseTestCase):
    def test_boolean(self):
        self.assertTrue(self.is_manager.model)
        self.assertTrue(self.is_manager.field)
        self.assertEqual(self.is_manager.datatype, 'boolean')

    def test_integer(self):
        self.assertTrue(self.salary.model)
        self.assertTrue(self.salary.field)
        self.assertEqual(self.salary.datatype, 'number')

    def test_string(self):
        self.assertTrue(self.first_name.model)
        self.assertTrue(self.first_name.field)
        self.assertEqual(self.first_name.datatype, 'string')


class DataConceptTestCase(BaseTestCase):
    def test_search(self):
        management.call_command('rebuild_index', interactive=False)


class DataCategoryTestCase(BaseTestCase):
    pass

from django.test import TestCase
from django.core import management
from haystack.query import RelatedSearchQuerySet
from avocado.models import DataField, DataConcept


class SearchTest(TestCase):
    fixtures = ['search.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'search', quiet=True)
        management.call_command('rebuild_index', interactive=False,
                                verbosity=0)


class FieldSearchTest(SearchTest):
    def test_empty(self):
        self.assertEqual(len(DataField.objects.published()), 12)
        self.assertEqual(RelatedSearchQuerySet().models(DataField).count(), 12)
        self.assertEqual(len(DataField.objects.search('')), 12)

    def test_field_match(self):
        "Search on field-level properties (e.g. name)"
        location = DataField.objects.get_by_natural_key('search.office.location')
        boss = DataField.objects.get_by_natural_key('search.title.boss')
        salary = DataField.objects.get_by_natural_key('search.title.salary')
        is_manager = DataField.objects.get_by_natural_key('search.employee.is_manager')

        search = DataField.objects.search

        self.assertEqual(search('salary')[0].object, salary)
        self.assertEqual(search('location')[0].object, location)
        self.assertEqual(search('boss')[0].object, boss)
        self.assertEqual(search('manager')[0].object, is_manager)

    def test_model_match(self):
        "Search on model-level properties (e.g. name)"
        office_fields = sorted(list(DataField.objects.filter(model_name='office').values_list('pk', flat=True)))
        title_fields = sorted(list(DataField.objects.filter(model_name='title').values_list('pk', flat=True)))
        employee_fields = sorted(list(DataField.objects.filter(model_name='employee').values_list('pk', flat=True)))

        search = DataField.objects.search

        self.assertEqual(sorted([x.object.pk for x in search('office')]), office_fields)
        self.assertEqual(sorted([x.object.pk for x in search('title')]), title_fields)
        self.assertEqual(sorted([x.object.pk for x in search('employee')]), employee_fields)

    def test_data(self):
        "Test search via the data itself."
        fields = DataField.objects.all()

        # Ensure all enumerable, searchable fields match for every value
        # they contain
        for f in fields:
            if f.simple_type != 'boolean' and f.enumerable or f.searchable:
                for v in f.values():
                    self.assertTrue(f in [x.object for x in DataField.objects.search(v)])

    def test_partial(self):
        self.assertEqual(len(DataField.objects.search('Eri', partial=True)), 1)


class ConceptSearchTest(SearchTest):
    def test_field_match(self):
        "Search on field-level properties (e.g. name)"
        location = DataConcept.objects.get(name='Location')
        boss = DataConcept.objects.get(name='Boss')
        salary = DataConcept.objects.get(name='Salary')
        is_manager = DataConcept.objects.get(name='Is Manager')

        search = DataConcept.objects.search

        self.assertEqual(search('salary')[0].object, salary)
        self.assertEqual(search('location')[0].object, location)
        self.assertEqual(search('boss')[0].object, boss)
        self.assertEqual(search('manager')[0].object, is_manager)

    def test_model_match(self):
        "Search on model-level properties (e.g. name)"
        office_concepts = sorted(list(DataConcept.objects.filter(fields__model_name='office').values_list('pk', flat=True)))
        title_concepts = sorted(list(DataConcept.objects.filter(fields__model_name='title').values_list('pk', flat=True)))
        employee_concepts = sorted(list(DataConcept.objects.filter(fields__model_name='employee').values_list('pk', flat=True)))

        search = DataConcept.objects.search

        self.assertEqual(sorted([x.object.pk for x in search('office')]), office_concepts)
        self.assertEqual(sorted([x.object.pk for x in search('title')]), title_concepts)
        self.assertEqual(sorted([x.object.pk for x in search('employee')]), employee_concepts)

    def test_data(self):
        "Test search via the data itself."
        concepts = DataConcept.objects.all()

        # Ensure each concept match for a values for each associated field
        for c in concepts:
            for f in c.fields.all():
                if f.simple_type != 'boolean' and f.enumerable or f.searchable:
                    for v in f.values():
                        self.assertTrue(c in [x.object for x in DataConcept.objects.search(v)])

    def test_partial(self):
        self.assertEqual(len(DataConcept.objects.search('Eri', partial=True)), 1)

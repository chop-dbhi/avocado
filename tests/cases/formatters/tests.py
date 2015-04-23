from django.test import TestCase
from django.core import management
from avocado.models import DataField, DataConcept, DataConceptField
from avocado.formatters import Formatter


class FormatterTestCase(TestCase):
    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

        name_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'name')
        salary_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        boss_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'boss')

        concept = DataConcept(name='Title')
        concept.save()

        DataConceptField(concept=concept, field=name_field, order=1).save()
        DataConceptField(concept=concept, field=salary_field, order=2).save()
        DataConceptField(concept=concept, field=boss_field, order=3).save()

        self.concept = concept
        self.values = ['CEO', 100000, True]

    def test_fields(self):
        f = Formatter(self.concept)

        meta = f.get_meta()
        header = meta['header']
        self.assertEqual(3, len(header))

        names = [x['name'] for x in header]
        self.assertEqual(names, ['name', 'salary', 'boss'])

    def test_default(self):
        f = Formatter(self.concept)

        fvalues = f(self.values)
        expected = ('CEO', 100000, True)

        self.assertEqual(fvalues, expected)

    def test_to_string(self):
        f = Formatter(self.concept, formats=['string'])

        fvalues = f(self.values)
        expected = ('CEO', '100000', 'True')

        self.assertEqual(fvalues, expected)

    def test_to_number(self):
        f = Formatter(self.concept, formats=['number'])

        fvalues = f(self.values)
        expected = ('CEO', 100000, 1)

        self.assertEqual(fvalues, expected)

    def test_to_boolean(self):
        f = Formatter(self.concept, formats=['boolean'])

        fvalues = f(self.values)
        expected = ('CEO', 100000, True)

        self.assertEqual(fvalues, expected)

    def test_to_coded(self):
        f = Formatter(self.concept, formats=['coded'])

        fvalues = f(self.values)
        expected = ('CEO', 100000, 1)

        self.assertEqual(fvalues, expected)

    def test_to_html(self):
        class HtmlFormatter(Formatter):
            def to_html(self, values, fields, context):
                fvalues = []

                for i, k in enumerate(fields):
                    value = self.to_string(values[i], fields[k], context)
                    fvalues.append(value)

                return '<span>{0}</span>'.format('</span><span>'.join(fvalues))

            to_html.process_multiple = True

        f = HtmlFormatter(self.concept, formats=['html'])

        output = f(self.values)
        expected = u'<span>CEO</span><span>100000</span><span>True</span>'

        self.assertEqual(output[0], expected)

    def test_unique_keys(self):
        title_name = DataField.objects.get_by_natural_key(
            'tests', 'title', 'name')

        project_name = DataField.objects.get_by_natural_key(
            'tests', 'project', 'name')

        concept = DataConcept()
        concept.save()

        DataConceptField(concept=concept, field=title_name, order=1).save()
        DataConceptField(concept=concept, field=project_name, order=2).save()

        f = Formatter(concept=concept)

        meta = f.get_meta()
        names = [x['name'] for x in meta['header']]

        self.assertEqual(names, ['title__name', 'project__name'])

import os
from django.test import TestCase
from django.http import HttpResponse
from django.template import Template
from django.core import management
from avocado import export
from avocado.models import DataField, DataConcept, DataConceptField, DataView
from avocado.query.pipeline import QueryProcessor
from ... import models


html_table = """
<table>
    <thead>
        {% for f in header %}
            <th>{{ f.label }}</th>
        {% endfor %}
    </thead>
    <tbody>
        {% for row in rows %}
            <tr>
            {% for value in row %}
                <td>{{ value }}</td>
            {% endfor %}
            </tr>
        {% endfor %}
    </tbody>
</table>
"""

# Allowed delta in bytes for the AlmostEqual assertion.
delta = 20


class ExportTestCase(TestCase):
    fixtures = ['tests/fixtures/employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

        field = DataField.objects.get(field_name='salary')
        concept = field.concepts.all()[0]

        view = DataView(json=[{
            'concept': concept.pk,
            'visible': False,
            'sort': 'desc',
        }])

        self.pks = list(models.Employee.objects.values_list('pk', flat=True)
                        .order_by('-title__salary'))

        proc = QueryProcessor(view=view)
        queryset = proc.get_queryset()
        self.iterable = proc.get_iterable(queryset=queryset)
        self.exporter = proc.get_exporter(export.BaseExporter)

    def test_read(self):
        it = self.exporter.read(self.iterable)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks)

    def test_cached_read(self):
        it = self.exporter.cached_read(self.iterable)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks)

    def test_threaded_read(self):
        it = self.exporter.threaded_read(self.iterable)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks)

    def test_cached_threaded_read(self):
        it = self.exporter.cached_threaded_read(self.iterable)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks)

    def test_manual_read(self):
        it = self.exporter.manual_read(self.iterable)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks)

    def test_read_offset(self):
        it = self.exporter.manual_read(self.iterable, offset=2)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks[2:])

    def test_read_limit(self):
        it = self.exporter.manual_read(self.iterable, limit=2)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks[:2])

    def test_read_limit_offset(self):
        it = self.exporter.manual_read(self.iterable, limit=2, offset=2)
        rows = list(it)
        self.assertEqual([r[0] for r in rows], self.pks[2:4])

    def test_write(self):
        it = self.exporter.read(self.iterable)
        rows = list(self.exporter.write(it))
        self.assertEqual([r[0] for r in rows], self.pks)


class FileExportTestCase(TestCase):
    fixtures = ['tests/fixtures/employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

        first_name_field = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'first_name')
        first_name_field.description = 'First Name'
        first_name_field.save()

        last_name_field = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'last_name')
        last_name_field.description = 'Last Name'
        last_name_field.save()

        title_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'name')
        title_field.description = 'Employee Title'
        title_field.save()

        salary_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        salary_field.description = 'Salary'
        salary_field.save()

        is_manager_field = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')
        is_manager_field.description = 'Is a Manager?'
        is_manager_field.save()

        employee_concept = DataConcept()
        employee_concept.name = 'Employee'
        employee_concept.description = 'A Single Employee'
        employee_concept.save()

        DataConceptField(
            concept=employee_concept, field=first_name_field, order=1).save()
        DataConceptField(
            concept=employee_concept, field=last_name_field, order=2).save()
        DataConceptField(
            concept=employee_concept, field=is_manager_field, order=3).save()
        DataConceptField(
            concept=employee_concept, field=title_field, order=4).save()
        DataConceptField(
            concept=employee_concept, field=salary_field, order=5).save()

        self.concepts = [employee_concept]

        self.query = models.Employee.objects.values_list(
            'first_name', 'last_name', 'is_manager', 'title__name',
            'title__salary')

    def test_csv(self):
        name = 'export.csv'
        exp_size = 250

        exporter = export.CSVExporter(self.concepts)
        it = exporter.read(self.query)

        exporter.write(it, buff=name)

        size = os.path.getsize(name)
        self.assertAlmostEqual(size, exp_size, delta=delta)

        os.remove(name)

    def test_excel(self):
        name = 'excel_export.xlsx'
        exp_size = 6086

        exporter = export.ExcelExporter(self.concepts)
        it = exporter.read(self.query)
        exporter.write(it, buff=name)

        size = os.path.getsize(name)
        self.assertAlmostEqual(size, exp_size, delta=delta)

        os.remove(name)

    def test_sas(self):
        name = 'sas_export.zip'
        exp_size = 1340

        exporter = export.SASExporter(self.concepts)
        it = exporter.read(self.query)
        exporter.write(it, buff=name)

        size = os.path.getsize(name)
        self.assertAlmostEqual(size, exp_size, delta=delta)

        os.remove(name)

    def test_r(self):
        name = 'r_export.zip'
        exp_size = 760

        exporter = export.RExporter(self.concepts)
        it = exporter.read(self.query)
        exporter.write(it, buff=name)

        size = os.path.getsize(name)
        self.assertAlmostEqual(size, exp_size, delta=delta)

        os.remove(name)

    def test_json(self):
        name = 'export.json'
        exp_size = 630

        exporter = export.JSONExporter(self.concepts)
        it = exporter.read(self.query)

        exporter.write(it, buff=name)

        size = os.path.getsize(name)
        self.assertAlmostEqual(size, exp_size, delta=delta)

        os.remove(name)

    def test_html(self):
        name = 'export.html'
        exp_size = 892

        template = Template(html_table)
        exporter = export.HTMLExporter(self.concepts)
        it = exporter.read(self.query)

        exporter.write(it, buff=name, template=template)

        size = os.path.getsize(name)
        self.assertAlmostEqual(size, exp_size, delta=delta)

        os.remove(name)


class ResponseExportTestCase(FileExportTestCase):
    def test_csv(self):
        exp_size = 240

        response = HttpResponse()
        exporter = export.CSVExporter(self.concepts)

        it = exporter.read(self.query)
        exporter.write(it, buff=response)

        self.assertAlmostEqual(len(response.content), exp_size, delta=delta)

    def test_excel(self):
        exp_size = 6086

        response = HttpResponse()
        exporter = export.ExcelExporter(self.concepts)

        it = exporter.read(self.query)
        exporter.write(it, buff=response)

        self.assertAlmostEqual(len(response.content), exp_size, delta=delta)

    def test_sas(self):
        exp_size = 1340

        response = HttpResponse()
        exporter = export.SASExporter(self.concepts)

        it = exporter.read(self.query)
        exporter.write(it, buff=response)

        self.assertAlmostEqual(len(response.content), exp_size, delta=delta)

    def test_r(self):
        exp_size = 760

        response = HttpResponse()
        exporter = export.RExporter(self.concepts)

        it = exporter.read(self.query)
        exporter.write(it, buff=response)

        self.assertAlmostEqual(len(response.content), exp_size, delta=delta)

    def test_json(self):
        exp_size = 630

        response = HttpResponse()
        exporter = export.JSONExporter(self.concepts)

        it = exporter.read(self.query)
        exporter.write(it, buff=response)

        self.assertAlmostEqual(len(response.content), exp_size, delta=delta)

    def test_html(self):
        exp_size = 892

        response = HttpResponse()
        exporter = export.HTMLExporter(self.concepts)
        template = Template(html_table)

        it = exporter.read(self.query)
        exporter.write(it, buff=response, template=template)

        self.assertAlmostEqual(len(response.content), exp_size, delta=delta)


class ForceDistinctRegressionTestCase(TestCase):
    fixtures = ['tests/fixtures/employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)

        self.first_name = DataField.objects.get(field_name='first_name')\
            .concepts.all()[0]
        self.last_name = DataField.objects.get(field_name='last_name')\
            .concepts.all()[0]
        self.project_name = DataField.objects\
            .get(model_name='project', field_name='name')\
            .concepts.all()[0]
        self.title_name = DataField.objects\
            .get(model_name='title', field_name='name')\
            .concepts.all()[0]

        e1 = models.Employee.objects.get(pk=1)
        e2 = models.Employee.objects.get(pk=2)

        p1 = models.Project(name='P1', manager=e1)
        p1.save()

        p2 = models.Project(name='P2', manager=e2)
        p2.save()

        p1.employees = [e1, e2]
        p2.employees = [e1, e2]

    def test_sort_flat(self):
        "Sorts on a non-reverse foreign key property."
        view = DataView(json=[
            {'concept': self.first_name.pk},
            {'concept': self.last_name.pk},
            {'concept': self.title_name.pk, 'sort': 'desc', 'visible': False},
        ])

        proc = QueryProcessor(view=view)
        queryset = proc.get_queryset()
        exporter = proc.get_exporter(export.BaseExporter)

        iterable = proc.get_iterable(queryset=queryset)
        reader = exporter.manual_read(iterable)

        self.assertEqual(list(exporter.write(reader)), [
            (1, u'Eric', u'Smith'),
            (3, u'Erick', u'Smith'),
            (5, u'Zac', u'Cook'),
            (2, u'Erin', u'Jones'),
            (4, u'Aaron', u'Harris'),
            (6, u'Mel', u'Brooks'),
        ])

    def test_sort_related(self):
        "Sorts on a reverse foreign key property."
        view = DataView(json=[
            {'concept': self.first_name.pk},
            {'concept': self.last_name.pk},
            {'concept': self.project_name.pk, 'sort': 'asc', 'visible': False},
        ])

        proc = QueryProcessor(view=view)
        queryset = proc.get_queryset()
        exporter = proc.get_exporter(export.BaseExporter)

        iterable = proc.get_iterable(queryset=queryset)
        reader = exporter.manual_read(iterable)

        self.assertEqual(list(exporter.write(reader)), [
            (3, u'Erick', u'Smith'),
            (4, u'Aaron', u'Harris'),
            (5, u'Zac', u'Cook'),
            (6, u'Mel', u'Brooks'),
            (1, u'Eric', u'Smith'),
            (2, u'Erin', u'Jones')
        ])

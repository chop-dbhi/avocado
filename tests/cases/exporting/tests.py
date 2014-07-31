import os
from django.test import TestCase
from django.http import HttpResponse
from django.template import Template
from django.core import management
from avocado import export
from avocado.formatters import RawFormatter
from avocado.models import DataField, DataConcept, DataConceptField, DataView
from ... import models

__all__ = ['FileExportTestCase', 'ResponseExportTestCase',
           'ForceDistinctRegressionTestCase']


class ExportTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)
        salary_concept = \
            DataField.objects.get(field_name='salary').concepts.all()[0]

        view = DataView(json={'ordering': [[salary_concept.pk, 'desc']]})
        self.query = view.apply(tree=models.Employee).raw()
        # Ick..
        self.exporter = export.BaseExporter(view)
        self.exporter.params.insert(0, (RawFormatter(keys=['pk']), 1))
        self.exporter.row_length += 1

    def test(self):
        rows = list(self.exporter.write(self.query))
        self.assertEqual([r[0] for r in rows], [2, 4, 6, 1, 3, 5])

    def test_offset(self):
        rows = list(self.exporter.write(self.query, offset=2))
        self.assertEqual([r[0] for r in rows], [6, 1, 3, 5])

    def test_limit(self):
        rows = list(self.exporter.write(self.query, limit=2))
        self.assertEqual([r[0] for r in rows], [2, 4])

    def test_limit_offset(self):
        rows = list(self.exporter.write(self.query, offset=2, limit=2))
        self.assertEqual([r[0] for r in rows], [6, 1])


class FileExportTestCase(TestCase):
    fixtures = ['employee_data.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'tests', quiet=True)
        first_name_field = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'first_name')
        first_name_field.description = 'First Name'
        last_name_field = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'last_name')
        last_name_field.description = 'Last Name'
        title_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'name')
        title_field.description = 'Employee Title'
        salary_field = DataField.objects.get_by_natural_key(
            'tests', 'title', 'salary')
        salary_field.description = 'Salary'
        is_manager_field = DataField.objects.get_by_natural_key(
            'tests', 'employee', 'is_manager')
        is_manager_field.description = 'Is a Manager?'

        [x.save() for x in [first_name_field, last_name_field, title_field,
                            salary_field, is_manager_field]]

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
        exporter = export.CSVExporter(self.concepts)
        buff = exporter.write(self.query)
        buff.seek(0)
        self.assertEqual(len(buff.read()), 246)

    def test_excel(self):
        fname = 'excel_export.xlsx'
        exporter = export.ExcelExporter(self.concepts)
        exporter.write(self.query, fname)
        self.assertTrue(os.path.exists(fname))
        # Observed slight size differences..
        l = len(open(fname).read())
        self.assertTrue(6220 <= l <= 6250)
        os.remove(fname)

    def test_sas(self):
        fname = 'sas_export.zip'
        exporter = export.SASExporter(self.concepts)
        exporter.write(self.query, fname)
        self.assertTrue(os.path.exists(fname))
        self.assertEqual(len(open(fname).read()), 1335)
        os.remove(fname)

    def test_r(self):
        fname = 'r_export.zip'
        exporter = export.RExporter(self.concepts)
        exporter.write(self.query, fname)
        self.assertTrue(os.path.exists(fname))
        self.assertEqual(len(open(fname).read()), 754)
        os.remove(fname)

    def test_json(self):
        exporter = export.JSONExporter(self.concepts)
        buff = exporter.write(self.query)
        buff.seek(0)
        self.assertEqual(len(buff.read()), 639)

    def test_html(self):
        exporter = export.HTMLExporter(self.concepts)
        template = Template("""<table>
{% for row in rows %}
    <tr>
    {% for item in row %}
        <td>{{ item.values|join:" " }}</td>
    {% endfor %}
    </tr>
{% endfor %}
</table>""")
        buff = exporter.write(self.query, template=template)
        buff.seek(0)
        self.assertEqual(len(buff.read()), 494)


class ResponseExportTestCase(FileExportTestCase):
    def test_csv(self):
        exporter = export.CSVExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 246)

    def test_excel(self):
        exporter = export.ExcelExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        # Observed slight size differences..
        l = len(response.content)
        self.assertTrue(6220 <= l <= 6250)

    def test_sas(self):
        exporter = export.SASExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 1335)

    def test_r(self):
        exporter = export.RExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 754)

    def test_json(self):
        exporter = export.JSONExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 639)

    def test_html(self):
        exporter = export.HTMLExporter(self.concepts)
        response = HttpResponse()
        template = Template("""<table>
{% for row in rows %}
    <tr>
    {% for item in row %}
        <td>{{ item.values|join:" " }}</td>
    {% endfor %}
    </tr>
{% endfor %}
</table>""")
        exporter.write(self.query, template=template, buff=response)
        self.assertEqual(len(response.content), 494)


class ForceDistinctRegressionTestCase(TestCase):
    fixtures = ['employee_data.json']

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

        queryset = view.apply()

        exporter = export.BaseExporter(view)
        exporter.params.insert(0, (RawFormatter(keys=['pk']), 1))
        exporter.row_length += 1

        self.assertEqual(list(exporter.write(queryset.raw())), [
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

        queryset = view.apply()

        exporter = export.BaseExporter(view)
        exporter.params.insert(0, (RawFormatter(keys=['pk']), 1))
        exporter.row_length += 1

        self.assertEqual(list(exporter.write(queryset.raw())), [
            (3, u'Erick', u'Smith'),
            (4, u'Aaron', u'Harris'),
            (5, u'Zac', u'Cook'),
            (6, u'Mel', u'Brooks'),
            (1, u'Eric', u'Smith'),
            (2, u'Erin', u'Jones')
        ])

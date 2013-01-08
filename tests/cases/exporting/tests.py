import os
from django.test import TestCase
from django.http import HttpResponse
from django.template import Template
from django.core import management
from avocado import export
from avocado.models import DataField, DataConcept, DataConceptField
from . import models

__all__ = ['FileExportTestCase', 'ResponseExportTestCase']


class FileExportTestCase(TestCase):
    fixtures = ['export.json']

    def setUp(self):
        management.call_command('avocado', 'init', 'exporting', quiet=True)
        first_name_field = DataField.objects.get_by_natural_key('exporting', 'employee', 'first_name')
        first_name_field.description = 'First Name'
        last_name_field = DataField.objects.get_by_natural_key('exporting', 'employee', 'last_name')
        last_name_field.description = 'Last Name'
        title_field = DataField.objects.get_by_natural_key('exporting', 'title', 'name')
        title_field.description = 'Employee Title'
        salary_field = DataField.objects.get_by_natural_key('exporting', 'title', 'salary')
        salary_field.description = 'Salary'
        is_manager_field = DataField.objects.get_by_natural_key('exporting', 'employee', 'is_manager')
        is_manager_field.description = 'Is a Manager?'

        [x.save() for x in [first_name_field, last_name_field, title_field,
            salary_field, is_manager_field]]

        employee_concept = DataConcept()
        employee_concept.name = 'Employee'
        employee_concept.description = 'A Single Employee'
        employee_concept.save()

        DataConceptField(concept=employee_concept, field=first_name_field, order=1).save()
        DataConceptField(concept=employee_concept, field=last_name_field, order=2).save()
        DataConceptField(concept=employee_concept, field=is_manager_field, order=3).save()
        DataConceptField(concept=employee_concept, field=title_field, order=4).save()
        DataConceptField(concept=employee_concept, field=salary_field, order=5).save()

        self.concepts = [employee_concept]

        self.query = models.Employee.objects.values_list('first_name', 'last_name',
                'is_manager', 'title__name', 'title__salary')

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
        self.assertTrue(6220 <= l <= 6240)
        os.remove(fname)

    def test_sas(self):
        fname = 'sas_export.zip'
        exporter = export.SASExporter(self.concepts)
        exporter.write(self.query, fname)
        self.assertTrue(os.path.exists(fname))
        self.assertEqual(len(open(fname).read()), 1374)
        os.remove(fname)

    def test_r(self):
        fname = 'r_export.zip'
        exporter = export.RExporter(self.concepts)
        exporter.write(self.query, fname)
        self.assertTrue(os.path.exists(fname))
        self.assertEqual(len(open(fname).read()), 793)
        os.remove(fname)

    def test_json(self):
        exporter = export.JSONExporter(self.concepts)
        buff = exporter.write(self.query)
        buff.seek(0)
        self.assertEqual(len(buff.read()), 651)

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
        self.assertTrue(6220 <= l <= 6240)

    def test_sas(self):
        exporter = export.SASExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 1374)

    def test_r(self):
        exporter = export.RExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 793)

    def test_json(self):
        exporter = export.JSONExporter(self.concepts)
        response = HttpResponse()
        exporter.write(self.query, response)
        self.assertEqual(len(response.content), 651)

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

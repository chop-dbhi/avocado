import os
import unittest
from avocado.tests.base import BaseTestCase
from avocado import export

__all__ = ['ExportTestCase']


class ExportTestCase(BaseTestCase):
    def setUp(self):
        from avocado.tests import models
        from avocado.models import DataField, DataConcept, DataConceptField
        super(ExportTestCase, self).setUp()

        first_name_field = DataField.objects.get_by_natural_key('tests', 'employee', 'first_name')
        first_name_field.description = 'First Name'
        last_name_field = DataField.objects.get_by_natural_key('tests', 'employee', 'last_name')
        last_name_field.description = 'Last Name'
        title_field = DataField.objects.get_by_natural_key('tests', 'title', 'name')
        title_field.description = 'Employee Title'
        salary_field = DataField.objects.get_by_natural_key('tests', 'title', 'salary')
        salary_field.description = 'Salary'
        is_manager_field = DataField.objects.get_by_natural_key('tests', 'employee', 'is_manager')
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
        self.assertEqual(buff.read(), 'first_name,last_name,is_manager,name,salary\r\nEric,Smith,True,Programmer,15000\r\nErin,Jones,False,Analyst,20000\r\nErick,Smith,False,Programmer,15000\r\nAaron,Harris,False,Analyst,20000\r\nZac,Cook,False,Programmer,15000\r\nMel,Brooks,False,Analyst,20000\r\n')

    # Skip test if deps are not installed
    @unittest.skipUnless(export.ExcelExporter, 'openpyxl must be installed to test ExcelExporter')
    def test_excel(self):
        exporter = export.ExcelExporter(self.concepts)
        exporter.write(self.query, 'excel_export.xlsx')
        self.assertTrue(os.path.exists('excel_export.xlsx'))
        os.remove('excel_export.xlsx')

    def test_sas(self):
        exporter = export.SasExporter(self.concepts)
        exporter.write(self.query, 'sas_export.zip')
        self.assertTrue(os.path.exists('sas_export.zip'))
        os.remove('sas_export.zip')

    def test_r(self):
        exporter = export.RExporter(self.concepts)
        exporter.write(self.query, 'r_export.zip')
        self.assertTrue(os.path.exists('r_export.zip'))
        os.remove('r_export.zip')

    def test_json(self):
        exporter = export.JSONExporter(self.concepts)
        buff = exporter.write(self.query)
        buff.seek(0)
        self.assertEqual(buff.read(), '[[{"first_name": "Eric", "last_name": "Smith", "is_manager": "True", "name": "Programmer", "salary": 15000}], [{"first_name": "Erin", "last_name": "Jones", "is_manager": "False", "name": "Analyst", "salary": 20000}], [{"first_name": "Erick", "last_name": "Smith", "is_manager": "False", "name": "Programmer", "salary": 15000}], [{"first_name": "Aaron", "last_name": "Harris", "is_manager": "False", "name": "Analyst", "salary": 20000}], [{"first_name": "Zac", "last_name": "Cook", "is_manager": "False", "name": "Programmer", "salary": 15000}], [{"first_name": "Mel", "last_name": "Brooks", "is_manager": "False", "name": "Analyst", "salary": 20000}]]')

    def test_html(self):
        from django.template import Template
        exporter = export.HTMLExporter(self.concepts)
        template = Template("""<table>
{% for row in rows %}
    <tr>
    {% for item in row %}
        <td>{{ item.values|join:" " }}</td>
    {% endfor %}
{% endfor %}
</table>""")
        self.assertEqual(exporter.write(self.query, template=template), '<table>\n\n    <tr>\n    \n        <td>Eric Smith True Programmer 15000</td>\n    \n\n    <tr>\n    \n        <td>Erin Jones False Analyst 20000</td>\n    \n\n    <tr>\n    \n        <td>Erick Smith False Programmer 15000</td>\n    \n\n    <tr>\n    \n        <td>Aaron Harris False Analyst 20000</td>\n    \n\n    <tr>\n    \n        <td>Zac Cook False Programmer 15000</td>\n    \n\n    <tr>\n    \n        <td>Mel Brooks False Analyst 20000</td>\n    \n\n</table>')

import os
import unittest
from avocado.tests import models
from avocado.tests.base import BaseTestCase
from avocado.models import Field, Concept, ConceptField
from avocado import exporters

class ExportTestCase(BaseTestCase):
    def setUp(self):
        self.query = models.Employee.objects.all()

        first_name_field = Field.objects.get_by_natural_key('tests', 'employee', 'first_name')
        first_name_field.description = 'First Name'
        last_name_field = Field.objects.get_by_natural_key('tests', 'employee', 'last_name')
        last_name_field.description = 'Last Name'
        title_field = Field.objects.get_by_natural_key('tests', 'title', 'name')
        title_field.description = 'Employee Title'
        salary_field = Field.objects.get_by_natural_key('tests', 'title', 'salary')
        salary_field.description = 'Salary'
        is_manage_field = Field.objects.get_by_natural_key('tests', 'employee', 'is_manager')
        is_manage_field.description = 'Is a Manager?'

        [x.save() for x in [first_name_field, last_name_field, title_field,
            salary_field, is_manage_field]]

        employee_concept = Concept()
        employee_concept.name = 'Employee'
        employee_concept.description = 'A Single Employee'
        employee_concept.save()

        ConceptField(concept=employee_concept, field=first_name_field, order=1).save()
        ConceptField(concept=employee_concept, field=last_name_field, order=2).save()
        ConceptField(concept=employee_concept, field=is_manage_field, order=3).save()
        ConceptField(concept=employee_concept, field=title_field, order=4).save()
        ConceptField(concept=employee_concept, field=salary_field, order=5).save()

        self.concepts = [employee_concept]

    def test_csv(self):
        buff = open('csv_export.csv', 'wb+')
        exporter = exporters.CSVExporter(self.query, self.concepts)
        exporter.write(buff)
        buff.seek(0)
        self.assertEqual(buff.read(), 'first_name,last_name,is_manager,name,salary\r\nEric,Smith,1,Programmer,15000\r\nErin,Jones,0,Analyst,20000\r\nErick,Smith,0,Programmer,15000\r\nAaron,Harris,0,Analyst,20000\r\nZac,Cook,0,Programmer,15000\r\nMel,Brooks,0,Analyst,20000\r\n')
        os.remove('csv_export.csv')

    # Skip test if deps are not installed
    @unittest.skipUnless(exporters.ExcelExporter, 'openpyxl must be installed to test ExcelExporter')
    def test_excel(self):
        exporter = exporters.ExcelExporter(self.query, self.concepts)
        exporter.write('excel_export.xlsx', virtual=False)
        self.assertTrue(os.path.exists('excel_export.xlsx'))
        os.remove('excel_export.xlsx')

    def test_sas(self):
        exporter = exporters.SasExporter(self.query, self.concepts)
        exporter.write('sas_export.zip')
        self.assertTrue(os.path.exists('sas_export.zip'))
        os.remove('sas_export.zip')

    def test_r(self):
        exporter = exporters.RExporter(self.query, self.concepts)
        exporter.write('r_export.zip')
        self.assertTrue(os.path.exists('r_export.zip'))
        os.remove('r_export.zip')

    def test_json(self):
        exporter = exporters.JSONExporter(self.query, self.concepts)
        buff = open('json_export.json', 'wb+')
        exporter.write(buff)
        os.remove('json_export.json')


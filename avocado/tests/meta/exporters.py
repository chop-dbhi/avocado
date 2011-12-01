import os
from django.test import TestCase
from django.core.management import call_command
from avocado.meta.models import Field, Concept, ConceptField
from avocado.tests import models

from avocado.meta.exporters._base import BaseExporter
from avocado.meta.exporters._csv import CSVExporter
from avocado.meta.exporters._excel import ExcelExporter
from avocado.meta.exporters._sas import SasExporter
from avocado.meta.exporters._r import RExporter

class ExportTestCase(TestCase):
    fixtures = ['export_data.yaml']
    def setUp(self):
        call_command('avocado', 'sync', 'tests', verbosity=0)

        self.query = models.Employee.objects.all()

        first_name_field = Field.objects.get_by_natural_key('tests',
                'employee', 'first_name')
        first_name_field.description = 'First Name'
        last_name_field = Field.objects.get_by_natural_key('tests',
                'employee', 'last_name')
        last_name_field.description = 'Last Name'
        title_field = Field.objects.get_by_natural_key('tests',
            'title', 'name')
        title_field.description = 'Employee Title'
        salary_field = Field.objects.get_by_natural_key('tests',
            'title', 'salary')
        salary_field.description = 'Salary'
        is_manage_field = Field.objects.get_by_natural_key('tests',
            'employee', 'is_manager')
        is_manage_field.description = 'Is a Manager?'

        [x.save() for x in [first_name_field, last_name_field, title_field,
            salary_field, is_manage_field]]

        employee_concept = Concept()
        employee_concept.name = 'Employee'
        employee_concept.description = 'A Single Employee'
        employee_concept.save()

        ConceptField(concept=employee_concept,
                field=title_field, order=4).save()
        ConceptField(concept=employee_concept,
                field=salary_field, order=5).save()
        ConceptField(concept=employee_concept,
                field=first_name_field, order=1).save()
        ConceptField(concept=employee_concept,
                field=last_name_field, order=2).save()
        ConceptField(concept=employee_concept,
                field=is_manage_field, order=3).save()

        self.concepts = [employee_concept]

    def test_get_raw_query(self):
        exporter = BaseExporter(self.query, self.concepts)
        query = exporter._get_raw_query(self.concepts)
        self.assertEqual(query.sql, 'SELECT "tests_title"."name", "tests_title"."salary", "tests_employee"."first_name", "tests_employee"."last_name", "tests_employee"."is_manager" FROM "tests_employee" LEFT OUTER JOIN "tests_title" ON ("tests_employee"."title_id" = "tests_title"."id")')
          
    def test_csv(self):
        buff = open('csv_export.csv', 'wb+')
        exporter = CSVExporter(self.query, self.concepts)
        exporter.export(buff)
        buff.seek(0)
        self.assertEqual(buff.read(), 'name,salary,first_name,last_name,is_manager\r\nProgrammer,15000,Eric,Smith,1\r\nAnalyst,20000,Erin,Jones,0\r\nProgrammer,15000,Erick,Smith,0\r\nAnalyst,20000,Aaron,Harris,0\r\nProgrammer,15000,Zac,Cook,0\r\nAnalyst,20000,Mel,Brook,0\r\n')

    def test_excel(self):
        exporter = ExcelExporter(self.query, self.concepts)
        exporter.export('excel_export.xlsx', virtual=False)
        self.assertTrue(os.path.exists('excel_export.xlsx'))

    def test_sas(self):
        exporter = SasExporter(self.query, self.concepts)
        exporter.export('sas_export.zip')
        self.assertTrue(os.path.exists('sas_export.zip'))

    def test_r(self):
        exporter = RExporter(self.query, self.concepts)
        exporter.export('r_export.zip')
        self.assertTrue(os.path.exists('r_export.zip'))

from django.test import TestCase
from django import forms

from avocado.columns.models import Column
from avocado.fields.models import ModelField

__all__ = ('ModelFieldTestCase',)

class ModelFieldTestCase(TestCase):
    fixtures = ['test_data.yaml']
    
    def test_base(self):
        fc = ModelField.objects.get(pk=1)
        
        self.assertEqual(fc.model, Column)
        self.assertEqual(fc.field, Column._meta.get_field_by_name('name')[0])
        self.assertTrue(isinstance(fc.formfield(), forms.CharField))
    
    def test_formfield(self):
        fc = ModelField.objects.get(pk=3)
        
        self.assertTrue(isinstance(fc.formfield(), forms.CharField))
        self.assertTrue(isinstance(fc.formfield(formfield=forms.ChoiceField),
            forms.ChoiceField))
        
        fc.enable_choices = True
        
        ff = fc.formfield()
        self.assertTrue(isinstance(ff, forms.CharField))
        self.assertTrue(isinstance(ff.widget, forms.SelectMultiple))
    
    def test_choices(self):
        fc = ModelField.objects.get(pk=3)
        
        # choices not enabled
        self.assertEqual(fc.choices, None)
        
        fc.enable_choices = True
        del fc._choices
        
        # no callback specified
        self.assertEqual(fc.choices, [(u'f1', u'F1'), (u'f2', u'F2'),
            (u'f3', u'F3'), (u'f4', u'F4'), (u'f5', u'F5')])
        
        # evaluation
        del fc._choices
        
        fc.choices_handler = "(('foo', 'Foo'), ('bar', 'Bar'))"
        self.assertEqual(fc.choices, (('foo', 'Foo'), ('bar', 'Bar')))
        
        # test attr lookup on model
        del fc._choices
        
        SPECIAL_CHOICES = (('foo', 'Foo'), ('bar', 'Bar'))
        
        fc.choices_handler = 'SPECIAL_CHOICES'
        fc.model.SPECIAL_CHOICES = SPECIAL_CHOICES
        self.assertEqual(fc.choices, (('foo', 'Foo'), ('bar', 'Bar')))
        
        # test attr lookup on module
        del fc._choices
        del fc.model.SPECIAL_CHOICES
        
        module = __import__(fc.model.__module__)
        module.SPECIAL_CHOICES = SPECIAL_CHOICES
        self.assertEqual(fc.choices, (('foo', 'Foo'), ('bar', 'Bar')))
    
    # def test_coords(self):
    #     fc = ModelField.objects.get(pk=1)
    #     self.assertEqual(fc.coords, [(u'cc1', 1), (u'cc2', 1)])
        

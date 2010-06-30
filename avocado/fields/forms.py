from django import forms
from django.db import models
from django.db.models.fields import FieldDoesNotExist

from avocado.fields.models import FieldConcept

class FieldConceptAdminForm(forms.ModelForm):
    def clean_model_label(self):
        app_label, model_label = self.cleaned_data['model_label'].split('.')
        model = models.get_model(app_label, model_label)
    
        if model is None:
            raise forms.ValidationError, 'The model "%s" in the app "%s" does not ' \
                'exist' % (model_label, app_label)
        return self.cleaned_data['model_label']

    def clean(self):
        cleaned_data = super(FieldConceptAdminForm, self).clean()
        
        if cleaned_data.has_key('model_label') and cleaned_data.has_key('field_name'):
            app_label, model_label = cleaned_data['model_label'].split('.')
            model = models.get_model(app_label, model_label)
    
            field_name = cleaned_data['field_name']

            try:
                model._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                raise forms.ValidationError, 'The model "%s" does not have a field ' \
                    'named "%s"' % (model_label, field_name)
        
        return cleaned_data

    class Meta(object):
        model = FieldConcept
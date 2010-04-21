from django import forms
from django.db import models

from avocado.fields.models import FieldConcept

class FieldConceptAdminForm(forms.ModelForm):
    def clean_model_label(self):
        app_label, model_label = self.cleaned_data['model_label'].split('.')
        model = models.get_model(app_label, model_label)

        if model is None:
            raise forms.ValidationError, 'The model %s in app %s does not ' \
                'exist' % (model_label, app_label)
        return self.cleaned_data['model_label']

    def clean(self):
        cleaned_data = self.cleaned_data

        app_label, model_label = cleaned_data['model_label'].split('.')
        model = models.get_model(app_label, model_label)
        
        field_name = cleaned_data['field_name']

        if not hasattr(model, field_name) and \
            isinstance(getattr(model, field_name), models.Field):
            raise forms.ValidationError, 'The model %s does not have a field ' \
                'named %s' % (model_label, field_name)
        
        return cleaned_data

    class Meta:
        model = FieldConcept
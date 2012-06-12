from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from avocado.models import DataField


class DataFieldAdminForm(forms.ModelForm):
    def clean_app_name(self):
        app_name = self.cleaned_data.get('app_name')
        try:
            models.get_app(app_name)
        except ImproperlyConfigured:
            raise forms.ValidationError('The app "{}" could not be found'.format(app_name))
        return app_name

    def clean(self):
        cleaned_data = self.cleaned_data
        app_name = self.cleaned_data.get('app_name')
        model_name = cleaned_data.get('model_name')
        field_name = cleaned_data.get('field_name')

        model = models.get_model(app_name, model_name)
        if model is None:
            del cleaned_data['model_name']
            msg = 'The model "{}" could not be found in the app "{}"'.format(model_name, app_name)
            self._errors['model_name'] = self.error_class([msg])
        elif not model._meta.get_field_by_name(field_name):
            del cleaned_data['field_name']
            msg = 'The model "{}" does not have a field named "{}"'.format(model_name, field_name)
            self._errors['field_name'] = self.error_class([msg])
        return cleaned_data

    class Meta(object):
        model = DataField

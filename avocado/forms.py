from django import forms
from django.db import models
from avocado.models import DataField

class DataFieldAdminForm(forms.ModelForm):
    def clean_app_name(self):
        app_name = self.cleaned_data['app_name']
        if models.get_app(app_name) is None:
            raise forms.ValidationError('The app "{0}" could not be found'.format(app_name))
        return app_name

    def clean(self):
        cleaned_data = super(DataFieldAdminForm, self).clean()
        app_name = cleaned_data['app_name']

        # test `model_name'
        model_name = cleaned_data['model_name']
        if self.instance._get_model(app_name, model_name) is None:
            del cleaned_data['model_name']
            msg = 'The model "{0}" could not be found'.format(model_name)
            self._errors['model_name'] = self.error_class([msg])

        # test `field_name'
        field_name = cleaned_data['field_name']
        if self.instance._get_field(field_name) is None:
            del cleaned_data['field_name']
            msg = 'The model "{0}" does not have a field named "{1}"'.format(model_name, field_name)
            self._errors['field_name'] = self.error_class([msg])

        return cleaned_data

    class Meta(object):
        model = DataField

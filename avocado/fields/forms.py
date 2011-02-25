from django import forms
from django.db import models

from avocado.fields.models import Field

class FieldAdminForm(forms.ModelForm):

    def clean_app_name(self):
        app_name = self.cleaned_data['app_name']
        if models.get_app(app_name) is None:
            raise forms.ValidationError, 'The app "%s" could not be found' % app_name
        return app_name

    def clean(self):
        cleaned_data = super(FieldAdminForm, self).clean()

        app_name = cleaned_data['app_name']

        # test `model_name'
        model_name = cleaned_data['model_name']
        if self.instance._get_model(app_name, model_name) is None:
            del cleaned_data['model_name']
            msg = 'The model "%s" could not be found' % model_name
            self._errors['model_name'] = self.error_class([msg])

        # test `field_name'
        field_name = cleaned_data['field_name']
        if self.instance._get_field(field_name) is None:
            del cleaned_data['field_name']
            msg = 'The model "%s" does not have a field named "%s"' % \
                (model_name, field_name)
            self._errors['field_name'] = self.error_class([msg])

        # test `choices_handler'
        choices_handler = cleaned_data.get('choices_handler', None)
        if choices_handler and not self.instance._get_choices(choices_handler):
            del cleaned_data['choices_handler']
            msg = 'The choices could not be evaluated'
            self._errors['choices_handler'] = self.error_class([msg])

        return cleaned_data

    class Meta(object):
        model = Field

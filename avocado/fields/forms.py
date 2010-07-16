from django import forms

from avocado.fields.models import FieldConcept

class FieldConceptAdminForm(forms.ModelForm):
    def clean_model_label(self):
        model_label = self.cleaned_data['model_label']
        if self.instance._get_model(model_label) is None:
            raise forms.ValidationError, 'The model_label "%s" does not exist' % model_label
        return model_label
    
    def clean_coords_callback(self):
        coords_callback = self.cleaned_data['coords_callback']
        if self.instance._get_coords(coords_callback) is None:
            raise forms.ValidationError, 'Invalid SQL'
        return coords_callback
    
    def clean(self):
        cleaned_data = super(FieldConceptAdminForm, self).clean()
        
        model_label = cleaned_data['model_label']
        self.instance._get_model(model_label)

        # test `field_name'
        field_name = cleaned_data['field_name']
        if self.instance._get_field(field_name) is None:
            del cleaned_data['field_name']
            msg = 'The model "%s" does not have a field named "%s"' % \
                (self.model.__name__, field_name)
            self._errors['field_name'] = self.error_class([msg])
        
        # test `choices_handler'
        choices_handler = cleaned_data['choices_handler']
        if choices_handler and not self.instance._get_choices(choices_handler):
            del cleaned_data['choices_handler']
            msg = 'The choices could not be evaluated'
            self._errors['choices_handler'] = self.error_class([msg])
        
        return cleaned_data

    class Meta:
        model = FieldConcept
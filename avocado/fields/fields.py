from django import forms
from avocado.fields.widgets import RangeWidget

class RangeField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = (
            forms.CharField(),
            forms.CharField(required=False)
        )
        widget = kwargs.pop('widget', None) or RangeWidget()
        super(RangeField, self).__init__(fields=fields, widget=widget,
            **kwargs)
 
    def compress(self, data_list):
        return data_list

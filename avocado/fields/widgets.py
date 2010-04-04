from django import forms

class RangeWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        widgets=(forms.TextInput(attrs={'size': 5}),
            forms.TextInput(attrs={'size': 5}))
        super(RangeWidget, self).__init__(widgets)

    def decompress(self, value):
        return value or [u'', u'']


class DateRangeWidget(RangeWidget):
    def __init__(self, *args, **kwargs):
        widgets=(forms.TextInput(attrs={'class':'date', 'size': 10}),
            forms.TextInput(attrs={'class':'date', 'size': 10}))
        super(DateRangeWidget, self).__init__(widgets)

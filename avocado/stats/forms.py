from django import forms
from avocado.stats.models import Distribution


class DistributionForm(forms.ModelForm):
    class Meta(object):
        model = Distribution

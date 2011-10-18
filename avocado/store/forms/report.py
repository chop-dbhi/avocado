from django import forms
from django.db import transaction
from avocado.store.models import Report
from .context import ContextForm, SessionContextForm
from .scope import ScopeForm
from .perspective import PerspectiveForm

class ReportForm(ContextForm):
    scope = forms.Field(required=False)
    perspective = forms.Field(required=False)

    def clean_scope(self):
        if self.instance.pk:
            data = self.cleaned_data.get('scope')
            if data:
                form = ScopeForm(data, instance=self.instance.scope)
                if form.is_valid():
                    form.save(commit=False)
            return self.instance.scope

    def clean_perspective(self):
        if self.instance.pk:
            data = self.cleaned_data.get('perspective')
            if data:
                form = PerspectiveForm(data, instance=self.instance.perspective)
                if form.is_valid():
                    form.save(commit=False)
            return self.instance.perspective

    @transaction.commit_on_success
    def save(self, commit=True):
        instance = super(ReportForm, self).save(commit=False)
        if commit:
            instance.scope.save()
            instance.perspective.save()
            instance.save()
        return instance

    class Meta(ContextForm.Meta):
        model = Report
        fields = ('name', 'description', 'keywords', 'scope', 'perspective')


class SessionReportForm(SessionContextForm):
    class Meta(object):
        model = Report
        fields = ('name', 'description', 'keywords')

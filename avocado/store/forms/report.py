from django.db import transaction
from django import forms
from avocado.store.models import Report
from .context import ContextForm

class ReportForm(ContextForm):
    class Meta(ContextForm.Meta):
        model = Report


class SessionReportForm(forms.ModelForm):
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)

    def _fork(self, session_obj):
        new_report = session_obj.fork(exclude=('pk', 'reference', 'session'))

        new_scope = session_obj.scope.fork(commit=True, exclude=('pk', 'reference', 'session'))
        session_obj.scope.reference = new_scope
        session_obj.scope.save()

        new_perspective = session_obj.perspective.fork(commit=True, exclude=('pk', 'reference', 'session'))
        session_obj.perspective.reference = new_perspective
        session_obj.perspective.save()

        # update new report
        new_report.scope = new_scope
        new_report.perspective = new_perspective
        new_report.commit()

        session_obj.reference = new_report
        session_obj.save()

    @transaction.commit_on_success
    def save(self, commit=True):
        # apply changes to the session object
        session_obj = super(SessionReportForm, self).save(commit=False)

        # if no reference, but has been specified create a fork
        if not session_obj.reference and session_obj.name:
            self._fork(session_obj)
        # if a reference does exist and both the name and other stuff
        # has changed create a fork (not to overwrite an existing report)
        elif session_obj.has_changed() and session_obj.diff().get('name', None):
            self._fork(session_obj)
        # other simply save the session, 
        else:
            session_obj.save()

        return session_obj

    class Meta(object):
        model = Report
        fields = ('name', 'description', 'keywords')

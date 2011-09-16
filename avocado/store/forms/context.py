from django.db import transaction
from django import forms

class ContextForm(forms.ModelForm):
    name = forms.CharField()
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)

    class Meta(object):
        fields = ('name', 'description', 'keywords')


class SessionContextForm(ContextForm):
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)
    store = forms.Field(required=False)

    def _fork(self, session_obj):
        new_obj = session_obj.fork(commit=True, exclude=('pk', 'reference', 'session'))
        session_obj.reference = new_obj
        session_obj.save()

    @transaction.commit_on_success
    def save(self, commit=True):
        # apply changes to the session object
        session_obj = super(forms.ModelForm, self).save(commit=False)

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
        fields = ('name', 'description', 'keywords', 'store')

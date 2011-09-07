from django.db import transaction
from django import forms

class ContextForm(forms.ModelForm):

    name = forms.CharField()
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)

    # constructor takes an additional optional argument ``session_obj`` for
    # ensuring the session
    def __init__(self, *args, **kwargs):
        super(ContextForm, self).__init__(*args, **kwargs)
        if self.instance.session:
            raise Exception, 'use the SessionContextForm for the session object'

    def save(self, commit=True):
        obj = super(ContextForm, self).save(commit=False)
        if commit:
            obj.save(explicit=True)
        return obj

    class Meta(object):
        fields = ('name', 'description', 'keywords')


class SessionContextForm(ContextForm):

    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)
    store = forms.Field(required=False)

    def __init__(self, *args, **kwargs):
        super(SessionContextForm, self).__init__(*args, **kwargs)
        if not self.instance or not self.instance.session:
            raise Exception, 'use the ContextForm for the non-session objects'

    def _save_for_proxy(self, session_obj, obj, explicit=True):
        self._save(obj, explicit=True)
        session_obj.proxy(obj)
        session_obj.save(explicit=True)
        return obj

    def _save(self, obj, explicit):
        obj.save(explicit=explicit)
        self.save_m2m()
        return obj

    @transaction.commit_on_success
    def save(self, commit=True):
        # apply changes to the session object
        session_obj = super(forms.ModelForm, self).save(commit=False)

        # when a name is given, a new object must be created
        if self.cleaned_data.has_key('name'):
            # check if there is a session object available and if this instance
            # is the currently referenced object. if this object has changed
            # since the last explicit save, make a copy to same
            obj = session_obj.reference
            if not obj or obj.has_changed():
                obj = session_obj.copy()

            # if this is currently being referenced by the session, we need to
            # ensure the session object also reflects the current state of this
            # saved object.
            return self._save_for_proxy(session_obj, obj)

        # if this is the session object without a reference or a non-session
        # based processing of an object, perform an explicit save
        return self._save(session_obj, explicit=True)

    class Meta(object):
        fields = ('name', 'description', 'keywords', 'store')

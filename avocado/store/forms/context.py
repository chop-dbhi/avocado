from django.db import transaction
from django import forms

class ContextForm(forms.ModelForm):
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)

    class Meta(object):
        fields = ('name', 'description', 'keywords')


class SessionContextForm(ContextForm):
    # non-specific field..
    store = forms.Field(required=False)

    @transaction.commit_on_success
    def save(self, commit=True):
        # apply changes to the session object
        instance = super(SessionContextForm, self).save(commit=False)

        # if no reference, but a name has been specified create a fork
        if not instance.reference and instance.name:
            fork = instance.fork()
        # if a reference does exist and both the name and other stuff
        # has changed create a fork (not to overwrite an existing report)
        elif instance.has_changed() and instance.diff().get('name', None):
            fork = instance.fork()
        # other simply save the session,
        else:
            instance.save()

        return instance

    class Meta(object):
        fields = ('name', 'description', 'keywords', 'store')

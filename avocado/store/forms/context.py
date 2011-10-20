from django.db import transaction
from django import forms

class ContextForm(forms.ModelForm):
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    keywords = forms.CharField(required=False)
    store = forms.Field(required=False)

    class Meta(object):
        fields = ('name', 'description', 'keywords', 'store')


class SessionContextForm(ContextForm):
    @transaction.commit_on_success
    def save(self, commit=True):
        # shortcut for deferencing and clearing the session instance
        if not self.data and self.instance:
            # deference already saves the instance
            self.instance.deference()
            return self.instance

        # apply changes to the session object
        instance = super(SessionContextForm, self).save(commit=False)

        # if no reference, but a name has been specified create a fork
        if not instance.reference and instance.name:
            return instance.fork()
        elif instance.diff(fields=['name', 'description', 'keywords']):
            # if a reference does exist and both the name and other stuff
            # has changed create a fork (not to overwrite an existing report)
            if instance.has_changed():
                return instance.fork()
            # if it's just metadata that has changed, update the reference
            # in-place
            else:
                instance.push()

        instance.save()
        return instance

    class Meta(object):
        fields = ('name', 'description', 'keywords', 'store')

from django import forms
from django.db import models

from avocado.concepts.models import ConceptAbstract, ConceptFieldAbstract
from avocado.concepts.managers import ConceptManager
from avocado.fields.models import FieldConcept

__all__ = ('CriterionConcept', 'CriterionConceptField')

class CriterionConcept(ConceptAbstract):
    filter_name = models.CharField(max_length=100, null=True, blank=True)
    view_name = models.CharField(max_length=100, null=True, blank=True)
    template_name = models.CharField(max_length=100, null=True, blank=True)
    fields = models.ManyToManyField(FieldConcept, through='CriterionConceptField')

    objects = ConceptManager()

    class Meta(ConceptAbstract.Meta):
        verbose_name = 'criterion concept'
        verbose_name_plural = 'criterion concepts'

    def _get_form_class(self):
        if not hasattr(self, '_form_class'):
            form_fields = {}

            for f in self.fields.all():
                key = '%s_%s' % (f.id, f.field_name)
                form_fields[key] = f.formfield()

            class CriterionConceptForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    super(CriterionConceptForm, self).__init__(*args, **kwargs)
                    self.fields.update(form_fields)

            self._form_class = CriterionConceptForm
        return self._form_class
    form_class = property(_get_form_class)

    def is_valid(self, data, form_class=None):
        if form_class is None:
            form_class = self.form_class
        form = form_class(data)
        if form.is_valid():
            return True, form.cleaned_data
        return False, ()


class CriterionConceptField(ConceptFieldAbstract):
    concept = models.ForeignKey(CriterionConcept)

    class Meta(ConceptFieldAbstract.Meta):
        verbose_name = 'criterion concept field'
        verbose_name_plural = 'criterion concept fields'

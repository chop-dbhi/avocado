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

    def _get_form(self):
        if not hasattr(self, '_form'):
            from django import forms
            
            form_fields = {}
            
            for f in self.fields.all():
                key = '%s_%s' % (f.id, f.field_name)
                form_fields[key] = f.formfield(label=f.field_name)
            
            class CriterionConceptForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    super(CriterionConceptForm, self).__init__(*args, **kwargs)
                    self.fields.update(form_fields)
            
            self._form = CriterionConceptForm
        return self._form
    form = property(_get_form)

    def _get_view(self):
        if not hasattr(self, '_view'):
            from avocado.criteria.view import library
            self._view = library.get(self.view_name)
        return self._view
    view = property(_get_view)


class CriterionConceptField(ConceptFieldAbstract):
    concept = models.ForeignKey(CriterionConcept)

    class Meta(ConceptFieldAbstract.Meta):
        verbose_name = 'criterion concept field'
        verbose_name_plural = 'criterion concept fields'

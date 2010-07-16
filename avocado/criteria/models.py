from django import forms
from django.db import models

from avocado.concepts.models import Concept, ConceptField
from avocado.fields.models import FieldConcept
from avocado.criteria.viewset import library

__all__ = ('CriterionConcept', 'CriterionConceptField')

class CriterionConcept(Concept):
    fields = models.ManyToManyField(FieldConcept, through='CriterionConceptField')
    viewset = models.CharField(max_length=100, choices=library.choices())

    class Meta(Concept.Meta):
        verbose_name = 'criterion concept'
        verbose_name_plural = 'criterion concepts'

    def _get_form(self):
        if not hasattr(self, '_form'):
            from avocado.criteria.cache import cache
            form_fields = {}
            fields = cache.get_fields(self.id)

            for f in fields:
                form_fields[f.field_name] = f.formfield()

            class CriterionConceptForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    super(CriterionConceptForm, self).__init__(*args, **kwargs)
                    self.fields.update(form_fields)
            
            self._form = CriterionConceptForm
        return self._form
    form = property(_get_form)
    
    def _get_view_responses(self):
        if not hasattr(self, '_view_responses'):
            self._view_responses = library.get(self.viewset, self)
        return self._view_responses
    view_responses = property(_get_view_responses)


class CriterionConceptField(ConceptField):
    concept = models.ForeignKey(CriterionConcept)

    class Meta(ConceptField.Meta):
        verbose_name = 'criterion concept field'
        verbose_name_plural = 'criterion concept fields'

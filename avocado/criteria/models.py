from django import forms
from django.db import models

from avocado.concepts.models import Concept, ConceptField
from avocado.fields.models import FieldConcept
from avocado.criteria.mixins import CriterionConceptMixin

__all__ = ('CriterionConcept', 'CriterionConceptField')

class CriterionConcept(Concept, CriterionConceptMixin):
    fields = models.ManyToManyField(FieldConcept, through='CriterionConceptField')

    class Meta(Concept.Meta):
        verbose_name = 'criterion concept'
        verbose_name_plural = 'criterion concepts'

    def _get_form(self):
        if not hasattr(self, '_form'):
            form_fields = {}

            for f in self.fields.all():
                form_fields[f.field_name] = f.formfield()

            class CriterionConceptForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    super(CriterionConceptForm, self).__init__(*args, **kwargs)
                    self.fields.update(form_fields)

            self._form = CriterionConceptForm
        return self._form
    form = property(_get_form)


class CriterionConceptField(ConceptField):
    concept = models.ForeignKey(CriterionConcept)

    class Meta(ConceptField.Meta):
        verbose_name = 'criterion concept field'
        verbose_name_plural = 'criterion concept fields'

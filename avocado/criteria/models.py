from django import forms
from django.db import models

from avocado.settings import settings
from avocado.concepts.models import ConceptAbstract, ConceptFieldAbstract
from avocado.fields.models import FieldConcept

__all__ = ('CriterionConcept', 'CriterionConceptField')

CriterionConceptMixin = settings.CRITERION_CONCEPT_MIXIN

class CriterionConcept(ConceptAbstract, CriterionConceptMixin):
    filter_name = models.CharField(max_length=100, null=True, blank=True)
    fields = models.ManyToManyField(FieldConcept, through='CriterionConceptField')

    class Meta(ConceptAbstract.Meta):
        verbose_name = 'criterion concept'
        verbose_name_plural = 'criterion concepts'

    def _get_form(self):
        if not hasattr(self, '_form'):
            form_fields = {}

            for f in self.fields.all():
                key = '%s_%s' % (f.id, f.field_name)
                form_fields[key] = f.formfield()

            class CriterionConceptForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    super(CriterionConceptForm, self).__init__(*args, **kwargs)
                    self.fields.update(form_fields)

            self._form = CriterionConceptForm
        return self._form
    form = property(_get_form)


class CriterionConceptField(ConceptFieldAbstract):
    concept = models.ForeignKey(CriterionConcept)

    class Meta(ConceptFieldAbstract.Meta):
        verbose_name = 'criterion concept field'
        verbose_name_plural = 'criterion concept fields'

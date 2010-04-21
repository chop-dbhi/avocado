from django.db import models
from django import forms

from avocado.concepts.models import ConceptAbstract
from avocado.concepts.managers import ConceptManager

__all__ = ('FieldConcept',)

class FieldConcept(ConceptAbstract):
    """The `FieldConcept' class stores off meta data about a "field of
    interest" located on another model. This, in a sense, provides a way to
    specify the fields that can be utilized by the query engine.

    There three cases in which a "field of interest" should be stored:

        defintion/vocabulary - at the very least, storing off a field provides
        the ability specify a `description' and `keywords' (or aliases) associated
        with the field.

        search criteria - the field can be associated with one or more
        `CriterionConcepts'. at minimum, this provides the ability to query by
        this field. in a more complex scenario, the field can act as a dependent
        or dependency on other fields.

        reporting - the field can be associated with one or more `ColumnConcepts'
        which allows for generating reports (results) in-browser or exporting to
        another format.
    """
    model_label = models.CharField(max_length=100, editable=False)
    field_name = models.CharField(max_length=100, editable=False)
    formfield_class = models.CharField(max_length=100, editable=False)

    objects = ConceptManager()

    class Meta(ConceptAbstract.Meta):
        verbose_name = 'field concept'
        verbose_name_plural = 'field concepts'

    def __unicode__(self):
        return u'%s' % self.name or '.'.join([self.model_label, self.field_name])

    def _get_model(self):
        if not hasattr(self, '_model'):
            app_label, model_label = self.model_label.split('.')
            self._model = models.get_model(app_label, model_label)
        return self._model
    model = property(_get_model)

    def _get_field(self):
        if not hasattr(self, '_field'):
            self._field = self.model._meta.get_field_by_name(self.field_name)[0]
        return self._field
    field = property(_get_field)

    def formfield(self, **kwargs):
        return self.field.formfield(**kwargs)

    def value_is_valid(self, value, formfield=None, **kwargs):
        if formfield is None:
            formfield = self.field.formfield(**kwargs)
        
        print formfield.__class__
        try:
            cleaned_value = formfield.clean(value)
        except forms.ValidationError, e:
            return (False, None, e.messages)
        return (True, cleaned_value, ())

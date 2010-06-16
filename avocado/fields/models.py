from django.db import models
from django import forms

from avocado.concepts.models import ConceptAbstract
from avocado.concepts.managers import ConceptManager
from avocado.fields.operators import ValidationError

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
    field_type_name = models.CharField(max_length=100, null=True, blank=True)

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

    def _get_field_type(self):
        if not hasattr(self, '_field_type'):
            from avocado.fields import fieldtypes
            if self.field_type_name:
                self._field_type = getattr(fieldtypes, self.field_type_name)
            else:
                model_field_type = self.field.get_internal_type()
                self._field_type = fieldtypes.MODEL_FIELD_MAP[model_field_type]
        return self._field_type
    field_type = property(_get_field_type)

    def formfield(self, formfield=None, widget=None, **kwargs):
        "Returns the default `formfield' instance for the `field' type."
        if formfield is None:
            if self.field_type_name:
                formfield = self.field_type.field
            else:
                formfield = self.field.formfield

        if widget is None and self.field_type.widget_class:
            widget = self.field_type.widget_class()

        if 'label' in kwargs:
            label = kwargs.pop('label')
        else:
            label = self.field_name.title()
        
        return formfield(label=label, widget=widget, **kwargs)

    def clean(self, value, operator=None):
        """Cleans and validates the `operator' and `value' pair. It first tries
        to clean the `value' into the correct python object. This is done by
        fetching the default `formfield' class provided by the `field'
        instance.
        
        The second step is to validate the `operator' can be used for this
        instance's `field_type'. The `operator' also performs a minor
        cleaning that verifies the value is in the correct format for the
        operator.
        """
        formfield = self.formfield()

        if type(value) not in (list, tuple):
            value = [value]
            
        try:
            cleaned_value = map(formfield.clean, value)
        except forms.ValidationError, e:
            return (False, None, e.messages)
        
        try:
            cleaned_value = self.field_type.clean(cleaned_value)
        except ValidationError, e:
            return (False, None, e.message)

        return (True, cleaned_value, ())

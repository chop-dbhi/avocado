from django import forms
from django.db import models, transaction
from django.db.models import Count
from django.db.models.fields import FieldDoesNotExist
from django.db.utils import DatabaseError

from avocado.utils.iter import is_iter_not_string
from avocado.concepts.models import Concept
from avocado.fields.filters import library

__all__ = ('FieldConcept',)

class FieldConcept(Concept):
    """The `FieldConcept' class stores off meta data about a "field of
    interest" located on another model. This, in a sense, provides a way to
    specify the fields that can be utilized by the query engine.

    There three cases in which a "field of interest" should be stored:

        defintion/vocabulary - at the very least, storing off a field provides
        the ability specify a `description' and `keywords' (or aliases) associated
        with the field.

        queryability - the field can be associated with one or more
        `CriterionConcepts'. at minimum, this provides the ability to query by
        this field. in a more complex scenario, the field can act as a dependent
        or dependency on other fields.

        reporting - the field can be associated with one or more `ColumnConcepts'
        which allows for generating reports (results) in-browser or exporting to
        another format.
    """
    model_label = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    filter_name = models.CharField(max_length=100, choices=library.choices())
    enable_choices = models.BooleanField(default=False)
    choices_callback = models.TextField(null=True, blank=True, help_text="""
        Allowed callbacks include specifying:
            1. a constant name on the model
            2. a constant name on the model's module
            3. a string that can be evaluated
    """)

    class Meta(Concept.Meta):
        verbose_name = 'field concept'
        verbose_name_plural = 'field concepts'
        unique_together = ('model_label', 'field_name')

    def __unicode__(self):
        return u'%s' % self.name or '.'.join([self.model_label, self.field_name])

    def _get_module(self):
        if not hasattr(self, '_module'):
            self._module = __import__(self.model.__module__)
        return self._module
    module = property(_get_module)

    def _get_model(self, model_label=None):
        "Returns None if no model is found."
        if not hasattr(self, '_model') or model_label:
            model_label = model_label or self.model_label
            al, ml = model_label.split('.')
            self._model = models.get_model(al, ml)
        return self._model
    model = property(_get_model)

    def _get_field(self, field_name=None):
        if not hasattr(self, '_field') or field_name:
            field_name = field_name or self.field_name
            try:
                self._field = self.model._meta.get_field_by_name(field_name)[0]
            except FieldDoesNotExist:
                self._field = None
        return self._field
    field = property(_get_field)

    # TODO fix
    def _get_query_string(self, operator):
        nodes = modeltree.path_to(field.model)
        return modeltree.query_string(nodes, field.field_name, operator)

    def _get_choices(self, choices_callback=None):
        if not hasattr(self, '_choices') or choices_callback:
            self._choices = None
            if self.enable_choices or choices_callback:
                self._choices = ()
                choices_callback = choices_callback or self.choices_callback

                if not choices_callback:
                    name = self.field_name
                    choices = list(self.model.objects.values_list(name,
                        flat=True).order_by(name).distinct())
                    choices = zip(choices, map(lambda x: x.title(), choices))
                else:
                    from avocado.fields import parsers
                    funcs = (
                        (parsers.model_attr, (self.model, choices_callback)),
                        (parsers.module_attr, (self.module, choices_callback)),
                        (parsers.eval_choices, (choices_callback,)),
                    )

                    for func, attrs in funcs:
                        try:
                            choices = tuple(func(*attrs))
                            break
                        except TypeError:
                            pass
                    else:
                        choices = None
                self._choices = choices
        return self._choices
    choices = property(_get_choices)

    def _db_choices(self):
        if self.choices is not None:
            return map(lambda x: x[0], self.choices)

    def _get_coords(self, coords_callback=None):
        if not hasattr(self, '_coords') or coords_callback:
            coords_callback = coords_callback or self.coords_callback
            if coords_callback:
                from django.db import connections
                cursor = connections['default'].cursor()
                try:
                    cursor.execute(coords_callback)
                    coords = cursor.fetchall()
                except DatabaseError:
                    transaction.rollback()
                    coords = None
            else:
                name = self.field_name
                coords = self.model.objects.annotate(cnt=Count(name)).values_list(name, 'cnt')
            self._coords = coords
        return self._coords
    coords = property(_get_coords)

    def formfield(self, formfield=None, widget=None, **kwargs):
        "Returns the default `formfield' instance for the `field' type."
        if formfield is None:
            formfield = self.field.formfield

        if 'label' in kwargs:
            label = kwargs.pop('label')
        else:
            label = self.name.title()

        if not widget and self.enable_choices:
            widget = forms.SelectMultiple(choices=self.choices)

        return formfield(label=label, widget=widget, **kwargs)

    def clean_value(self, value, *args, **kwargs):
        """Cleans the supplied value with respect to the formfield. If
        `enable_choices' is true, it tests to ensure each value supplied
        is a valid choice.
        """
        field = self.formfield(*args, **kwargs)

        try:
            if is_iter_not_string(value):
                cleaned_value = map(field.clean, value)
            else:
                cleaned_value = field.clean(value)
        except forms.ValidationError, e:
            return (False, None, e.messages)


        if self.enable_choices:
            if not all(map(lambda x: x in self._db_choices, cleaned_value)):
                return (False, None, ('Value(s) supplied is not a valid choice'))

        return (True, cleaned_value, ())

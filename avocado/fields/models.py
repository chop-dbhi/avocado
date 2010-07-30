from django import forms
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import Group
from django.db.models.fields import FieldDoesNotExist

from avocado.settings import settings
from avocado.concepts.models import Category
from avocado.fields.translate import library

__all__ = ('ModelField',)

class ModelField(models.Model):
    """The `ModelField' class stores off meta data about a "field of
    interest" located on another model. This, in a sense, provides a way to
    specify the fields that can be utilized by the query engine.

    There are three cases in which a "field of interest" should be stored:

        defintion/vocabulary - at the very least, storing off a field provides
        the ability specify a `description' and `keywords' (or aliases) associated
        with the field.

        queryability - the field can be associated with one or more
        `Criterions'. at minimum, this provides the ability to query by
        this field. in a more complex scenario, the field can act as a dependent
        or dependency on other fields.

        reporting - the field can be associated with one or more `Columns'
        which allows for generating reports (results) in-browser or exporting to
        another format.
    """
    app_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    
    is_public = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, help_text='This ' \
        'ordering is relative to the category this concept belongs to.')

    # search optimizations
    search_doc = models.TextField(editable=False, null=True)

    if settings.ENABLE_GROUP_PERMISSIONS:
        groups = models.ManyToManyField(Group, blank=True)

    translator = models.CharField(max_length=100, choices=library.choices(),
        blank=True, null=True)

    # specify a constrained list of choices for this field, applies for
    # valiation and for display in the UI
    enable_choices = models.BooleanField(default=False)
    choices_handler = models.TextField(null=True, blank=True, help_text="""
        Allowed callbacks include specifying:
            1. a constant name on the model
            2. a constant name on the model's module
            3. a string that can be evaluated
    """)

    class Meta:
        app_label = u'avocado'
        verbose_name = 'model field'
        verbose_name_plural = 'model fields'
        unique_together = ('app_name', 'model_name', 'field_name')

    def __unicode__(self):
        if self.name:
            return u'%s' % self.name
        name = '.'.join([self.app_name, self.model_name, self.field_name])
        return u'%s' % name

    def _get_module(self):
        "Used for referencing `choices', if enabled."
        if not hasattr(self, '_module'):
            self._module = __import__(self.model.__module__)
        return self._module
    module = property(_get_module)

    def _get_model(self, app_name=None, model_name=None):
        "Returns None if no model is found."
        if not hasattr(self, '_model') or (app_name and model_name):
            app_name = app_name or self.app_name
            model_name = model_name or self.model_name
            self._model = models.get_model(app_name, model_name)
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

    def _get_choices(self, choices_handler=None):
        if not hasattr(self, '_choices') or choices_handler:
            choices = None
            if self.enable_choices:
                choices_handler = choices_handler or self.choices_handler

                # use introspection
                if not choices_handler:
                    name = self.field_name
                    choices = list(self.model.objects.values_list(name,
                        flat=True).order_by(name).distinct())
                    choices = zip(choices, map(lambda x: x.title(), choices))

                # attempt to evaluate custom handler
                else:
                    from avocado.fields import evaluators
                    choices = evaluators.evaluate(self)

            self._choices = choices
        return self._choices
    choices = property(_get_choices)

    def _get_raw_choices(self):
        if self.choices is not None:
            return map(lambda x: x[0], self.choices)
    raw_choices = property(_get_raw_choices)

    def reset_choices(self):
        if hasattr(self, '_choices'):
            delattr(self, '_choices')

    def distribution(self, exclude=[], **filters):
        name = self.field_name
        dist = self.model.objects.values(name)

        # exclude certain values (e.g. None, or (empty string))
        if exclude:
            kwarg = {str('%s__in' % name): exclude}
            dist = dist.exclude(**kwarg)

        if filters:
            dist = dist.filter(**filters)

        dist = dist.annotate(count=Count(name)).values_list(name, 'count')
        return list(dist)

    def query_string(self, operator, modeltree):
        nodes = modeltree.path_to(self.model)
        return modeltree.query_string(nodes, self.field_name, operator)

    def q(self, value, operator, modeltree):
        trans = library.get(self.translator)
        if trans is None:
            trans = library.default
        return trans(self, operator, value, modeltree)
    
    def query_by_value(self, value, operator, modeltree):
        q = self.q(value, operator, modeltree)
        return modeltree.root_model.objects.filter(q)
        
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

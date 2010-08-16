from django import forms
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import Group
from django.db.models.fields import FieldDoesNotExist

from avocado.conf import settings
from avocado.concepts.models import Category
from avocado.fields.translate import library

__all__ = ('Field',)

class Field(models.Model):
    """The `Field' class stores off meta data about a "field of
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
        unique_together = ('app_name', 'model_name', 'field_name')

    def __unicode__(self):
        if self.name:
            return u'%s' % self.name
        name = '.'.join([self.app_name, self.model_name, self.field_name])
        return u'%s' % name

    def _get_module(self):
        "Helper for determining ``choices``, if ``choices_handler`` is defined."
        if not hasattr(self, '_module'):
            self._module = __import__(self.model.__module__)
        return self._module
    module = property(_get_module)

    def _get_model(self, app_name=None, model_name=None):
        "Returns the model class this field is associated with."
        if not hasattr(self, '_model') or (app_name and model_name):
            app_name = app_name or self.app_name
            model_name = model_name or self.model_name
            self._model = models.get_model(app_name, model_name)
        return self._model
    model = property(_get_model)

    def _get_field(self, field_name=None):
        "Returns the field object from model."
        if not hasattr(self, '_field') or field_name:
            field_name = field_name or self.field_name
            try:
                self._field = self.model._meta.get_field_by_name(field_name)[0]
            except FieldDoesNotExist:
                self._field = None
        return self._field
    field = property(_get_field)

    def _get_choices(self, choices_handler=None):
        """Returns a distinct set of choices for this field.

        If a ``choices_handler`` is not defined, a distinct list of values are
        retrieved from the database.

        If ``choices_handler`` is defined, the handler is passed through a series
        of evaluators to try and convert it into a native object.
        """
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
        "Returns a list of the raw values."
        if self.choices is not None:
            return map(lambda x: x[0], self.choices)
    raw_choices = property(_get_raw_choices)

    def reset_choices(self):
        """This should be called when the ``_choices`` cache needs to be
        invalidated.
        """
        if hasattr(self, '_choices'):
            delattr(self, '_choices')

    def distribution(self, exclude=[], min_count=None, max_points=30,
        order_by='field', **filters):

        """Builds a GROUP BY queryset for use as a value distribution.

        ``exclude`` - a list of values to be excluded from the distribution. it
        may be desired to exclude NULL values or the empty string.

        .. note::

            the default behavior of the ``exclude`` argument is to do a SQL
            equivalent of NOT IN (...). if ``None`` is included, it will have
            a custom behavior of IS NOT NULL and will be removed from the IN
            clause. default is to include all values

        ``min_count`` - the minimum count for a particular value to be included
        in the distribution.

        ``max_points`` - the maximum number of points to be include in the
        distribution. the min and max values are always included, then a random
        sample is taken from the distribution. default is 30

        ``order_by`` - specify an ordering for the distribution. the choices are
        'count', 'field', or None. default is 'count'

        ``filters`` - a dict of filters to be applied to the queryset before
        the count annotation.
        """
        name = str(self.field_name)

        # get base queryset
        dist = self.model.objects.values(name)

        # exclude certain values (e.g. None, '')
        if exclude:
            exclude = set(exclude)
            kwargs = {}

            # special case for null values
            if None in exclude:
                kwargs['%s__isnull' % name] = True
                exclude.remove(None)

            kwargs['%s__in' % name] = exclude
            dist = dist.exclude(**kwargs)

        # apply filters before annotation is made
        if filters:
            dist = dist.filter(**filters)

        # apply annotation
        dist = dist.annotate(count=Count('id'))

        if min_count is not None and min_count > 1:
            dist = dist.exclude(count__lt=min_count)

        # evaluate
        dist = dist.values_list(name, 'count')

        # apply ordering
        if order_by == 'count':
            dist = dist.order_by('count')
        elif order_by == 'field':
            dist = dist.order_by(name)

        if max_points is not None:
            # TODO faster to do count or len?
            dist_len = dist.count()
            step = int(dist_len/max_points)

            if step > 1:
                # we can safely assume that this is NOT categorical data when
                # ``max_points`` is set and/or the condition where the count will
                # be greater than max_points will usually never be true
                dist = list(dist)

                # sample by step value
                sampled_dist = dist[::step]

                # if the last item was not included, include it to have the max
                if sampled_dist[-1] != dist[-1]:
                    sampled_dist.append(dist[-1])
                dist = sampled_dist

        return tuple(dist)

    def query_string(self, modeltree, operator=None):
        "Returns a django lookup string relative to the ``modeltree`` object."
        nodes = modeltree.path_to(self.model)
        return modeltree.query_string(nodes, self.field_name, operator)

    def order_string(self, modeltree, direction='asc'):
        qs = self.query_string(modeltree)
        if direction.lower() == 'desc':
            return '-' + qs
        return qs

    def translate(self, modeltree, operator=None, value=None, **context):
        trans = library.get(self.translator)
        if trans is None:
            trans = library.default
        return trans(modeltree, self, operator, value, **context)

    def query_by_value(self, modeltree, operator, value):
        q, ants = self.translate(modeltree, operator, value)
        qs = modeltree.root_model.objects.all()
        if ants:
            qs = qs.annotate(**ants)
        if q:
            qs = qs.filter(q)
        return qs

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

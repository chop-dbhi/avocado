from django.db import models
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site


# Field...

class Field(models.Model):
    app_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    is_public = models.BooleanField(default=False)
    group = models.ForeignKey(Group, null=True, blank=True)
    sites = models.ManyToManyField(Site, blank=True)

    translator = models.CharField(max_length=100, blank=True, null=True)

    enable_choices = models.BooleanField(default=False)

    choices_handler = models.TextField(null=True, blank=True, help_text="""
        Allowed callbacks include specifying:
            1. a constant name on the model
            2. a constant name on the model's module
            3. a string that can be evaluated
    """)

    class Meta(object):
        db_table = 'avocado_field'

    def __unicode__(self):
        return unicode(self.name)

    def natural_key(self):
        return self.app_name, self.model_name, self.field_name


# Category...

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True)
    order = models.FloatField(default=0)

    class Meta(object):
        db_table = 'avocado_category'

    def __unicode__(self):
        return unicode(self.name)


# Concepts...

class Concept(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    order = models.FloatField(default=0)

    class Meta(object):
        abstract = True

    def __unicode__(self):
        return unicode(self.name)


class ConceptField(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    order = models.FloatField(default=0)

    class Meta(object):
        abstract = True
        ordering = ('order',)

    def __unicode__(self):
        return unicode(self.field)


class Criterion(Concept):
    fields = models.ManyToManyField(Field, through='CriterionField')
    viewset = models.CharField(max_length=100)

    class Meta(Concept.Meta):
        db_table = 'avocado_criterion'


class CriterionField(ConceptField):
    concept = models.ForeignKey(Criterion, related_name='conceptfields')
    field = models.ForeignKey(Field, limit_choices_to={'is_public': True})
    required = models.BooleanField(default=True)

    class Meta(ConceptField.Meta):
        db_table = 'avocado_criterionfield'


class Column(Concept):
    "An interface to specify the necessary fields for a column."
    fields = models.ManyToManyField(Field, through='ColumnField')
    html_fmtr = models.CharField(max_length=100)
    csv_fmtr = models.CharField(max_length=100)

    class Meta(Concept.Meta):
        db_table = 'avocado_column'


class ColumnField(ConceptField):
    concept = models.ForeignKey(Column, related_name='conceptfields')
    field = models.ForeignKey(Field)

    class Meta(ConceptField.Meta):
        db_table = 'avocado_columnfield'

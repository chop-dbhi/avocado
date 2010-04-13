from django.db import models
from django.contrib.auth.models import Group

from avocado.fields.models import FieldConcept

__all__ = ('ConceptCategory', 'ConceptAbstract', 'ConceptFieldAbstract')

class ConceptCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta(object):
        app_label = 'avocado'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name


class ConceptAbstract(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    keywords = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(ConceptCategory)
    groups = models.ManyToManyField(Group, blank=True)
    is_public = models.BooleanField(default=True)

    # optimizations
    search_doc = models.TextField(editable=False)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name


class ConceptFieldAbstract(models.Model):
    order = models.SmallIntegerField(default=0)
    field = models.ForeignKey(FieldConcept)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('order',)

    def __unicode__(self):
        return u'%s' % self.field

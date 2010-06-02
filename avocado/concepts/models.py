from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings

__all__ = ('ConceptCategory', 'ConceptAbstract', 'ConceptFieldAbstract')

ENABLE_GROUP_PERMISSIONS = getattr(settings, 'AVOCADO_ENABLE_GROUP_PERMISSIONS', True)

class ConceptCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta(object):
        app_label = 'avocado'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name


class ConceptAbstract(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(ConceptCategory)
    is_public = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, help_text='This ' \
        'ordering is relative to the category this concept belongs to.')

    if ENABLE_GROUP_PERMISSIONS:
        groups = models.ManyToManyField(Group, null=True, blank=True)

    # search optimizations
    search_doc = models.TextField(editable=False, null=True)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name


class ConceptFieldAbstract(models.Model):
    from avocado.fields.models import FieldConcept

    order = models.SmallIntegerField(default=0)
    field = models.ForeignKey(FieldConcept)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('order',)

    def __unicode__(self):
        return u'%s' % self.field

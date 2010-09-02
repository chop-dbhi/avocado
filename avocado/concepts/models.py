from django.db import models

from avocado.concepts.managers import ConceptManager

__all__ = ('Category',)

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.FileField(upload_to='uploads/categories/')

    class Meta(object):
        verbose_name_plural = 'categories'
        app_label = 'avocado'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name


class Concept(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, help_text='This ' \
        'ordering is relative to the category this concept belongs to.')

    # search optimizations
    search_doc = models.TextField(editable=False, null=True)

    objects = ConceptManager()

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name


class ConceptField(models.Model):
    order = models.SmallIntegerField(default=0)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('order',)

    def __unicode__(self):
        return u'%s' % self.field

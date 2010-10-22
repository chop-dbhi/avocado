from django.db import models
from django.template import Template, Context

from avocado.concepts.managers import ConceptManager

__all__ = ('Category',)

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.FileField(upload_to='uploads/categories/', blank=True)

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
    order = models.FloatField(default=0, help_text='This ' \
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

    def full_description(self):
        if self.description:
            return self.description

        fields = list(self.fields.values('name', 'description')\
            .exclude(description=None))

        # don't bother with the template if only one field qualifies
        if len(fields) == 1:
            return fields[0]['description']

        t = Template("""
            {% for field in fields %}
                <strong>{{ field.name }}</strong> - {{ field.description }}
            {% endfor %}
            """)
        c = Context({'name': self.name, 'fields': fields})
        return t.render(c).strip()

class ConceptField(models.Model):
    order = models.FloatField(default=0)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('order',)

    def __unicode__(self):
        return u'%s' % self.field

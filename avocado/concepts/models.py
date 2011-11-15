from django.db import models
from django.db.models import Q
from django.template import Template, Context
from avocado.concepts.managers import ConceptManager

__all__ = ('Category',)

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True,
            related_name='children', limit_choices_to={'parent__isnull': True})
    order = models.FloatField(default=0)

    class Meta(object):
        verbose_name_plural = 'categories'
        app_label = 'avocado'
        ordering = ('order', 'name')

    def __unicode__(self):
        return u'%s' % self.name


class Concept(models.Model):
    # categories that do not have children or have a parent
    category_lookup = Q(children__isnull=True) | Q(parent__isnull=False)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True,
        limit_choices_to=category_lookup)
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
            fields = [{'name': self.name, 'description': self.description}]
        else:
            fields = list(self.conceptfields.select_related('field').values('name',
                'field__name', 'field__description').exclude(field__description=None))

            for x in fields:
                if x['name'] is None:
                    x['name'] = x.pop('field__name')
                x['description'] = x.pop('field__description').strip()

            # edge case when pretty field names are not set
            if len(fields) == 1:
                fields[0]['name'] = self.name

        c = Context({'fields': fields})
        t = Template("""
            {% load markup %}
            {% spaceless %}
            {% for field in fields %}
                {{ field.description|markdown }}
            {% endfor %}
            {% endspaceless %}
            """)
        return t.render(c).strip()


class ConceptField(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    order = models.FloatField(default=0)

    class Meta(object):
        abstract = True
        app_label = 'avocado'
        ordering = ('order',)

    def __unicode__(self):
        return u'%s' % self.field

from django.utils import termcolors
from django import template

register = template.Library()


@register.simple_tag
def colorize(value, *opts, **kwargs):
    return termcolors.colorize(value, opts=opts, **kwargs)

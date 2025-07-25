from django import template
from django.utils.text import slugify as dj_slugify
register = template.Library()

@register.filter
def slugify(value):
    return dj_slugify(value)

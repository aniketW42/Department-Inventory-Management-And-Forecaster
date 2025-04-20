from django import template

register = template.Library()

@register.filter
def sum(queryset, field_name):
    try:
        return sum(getattr(obj, field_name, 0) for obj in queryset)
    except Exception:
        return 0
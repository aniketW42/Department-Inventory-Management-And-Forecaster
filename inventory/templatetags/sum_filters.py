from django import template

register = template.Library()

@register.filter
def sum(queryset, field_name):
    try:
        return sum(getattr(obj, field_name, 0) for obj in queryset)
    except Exception:
        return 0
    
@register.filter
def sum_f(values):
    """
    Usage: {{ sequence|sum }} 
    Works for dict.values, lists, Querysets of numbers, etc.
    """
    if hasattr(values, "values"):  # if dict
        values = values.values()
    try:
        return int(__builtins__['sum']([int(v) for v in values if v is not None]))
    except Exception:
        return 0

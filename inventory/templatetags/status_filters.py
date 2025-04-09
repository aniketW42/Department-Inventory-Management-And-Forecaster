from django import template

register = template.Library()

@register.filter
def get_status_color(status):
    return {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'issued': 'primary',
        'returned': 'secondary'
    }.get(status, 'light')

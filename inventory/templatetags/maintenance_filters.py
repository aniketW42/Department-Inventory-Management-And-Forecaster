from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter
def days_until_maintenance(issue_date, interval_days):
    
    if not issue_date or not interval_days:
        return None

    # Convert datetime to date
    if hasattr(issue_date, 'date'):
        issue_date = issue_date.date()

    due_date = issue_date + timedelta(days=interval_days)
    return (due_date - date.today()).days


@register.filter
def is_under_maintenance(item):
    """
    Returns True if the item has any maintenance request in progress or pending.
    """
    active_statuses = ['pending', 'in_progress']
    return item.maintenance_logs.filter(status__in=active_statuses).exists()

from django.shortcuts import render
from .models import ItemRequest
import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

def item_maintenance(request):
    # Get search query and filter value from GET parameters
    search_query = request.GET.get('q', '')
    filter_value = request.GET.get('filter', '')

    # Start with the base query: items with 'issued' status
    issued_items = ItemRequest.objects.filter(status='issued').order_by('issued_date')
    issued_maintenance_items = issued_items.filter(item__needs_maintenance=True)
    # Filter by search query if provided
    if search_query:
        issued_maintenance_items = issued_maintenance_items.filter(Q(item__name__icontains=search_query))

    # Today's date
    today = timezone.now().date()

    # List to store filtered items
    filtered_items = []

    # Add custom logic to check if maintenance is overdue based on last_maintenance_date or issued_date
    for item in issued_maintenance_items:
        # Ensure last_maintenance_date is a date object
        last_maintenance_date = item.item.last_maintenance_date
        if last_maintenance_date and isinstance(last_maintenance_date, datetime.datetime):
            last_maintenance_date = last_maintenance_date.date()

        # Initialize is_overdue as False to avoid the "undefined variable" error
        is_overdue = False

        # If there's a last_maintenance_date
        if last_maintenance_date:
            # Calculate overdue based on last_maintenance_date
            if item.item.maintenance_interval_days is not None:
                days_since_last_maintenance = (today - last_maintenance_date).days
                is_overdue = days_since_last_maintenance > item.item.maintenance_interval_days
        else:
            # If there's no last_maintenance_date, calculate based on issued_date
            if item.item.maintenance_interval_days is not None:
                # Ensure issued_date is a date object (convert to date if it's a datetime object)
                issued_date = item.issued_date.date() if isinstance(item.issued_date, datetime.datetime) else item.issued_date


                days_since_issued = (today - issued_date).days
                is_overdue = days_since_issued > item.item.maintenance_interval_days

        # Filter based on the filter_value ('due' or 'overdue')
        if filter_value == 'overdue' and is_overdue:
            filtered_items.append(item)
        elif filter_value == 'due' and not is_overdue:
            filtered_items.append(item)
        elif filter_value == '':  # Show all non-overdue items when no filter is set
            filtered_items.append(item)

    # Paginate the filtered items
    paginator = Paginator(filtered_items, 30)
    page_number = request.GET.get('items_page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'maintenance/maintenance_page.html', {'maintenance_items': page_obj})

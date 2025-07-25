from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import InventoryItem, ItemRequest, MaintenanceRequest
from .utils import is_clerk

import datetime


# -------------------- Clerk View: Maintenance Overview --------------------

@login_required
@user_passes_test(is_clerk)
def item_maintenance(request):
    search_query = request.GET.get('q', '')
    filter_value = request.GET.get('filter', '')

    # Get all issued item requests where the item needs maintenance
    issued_requests = ItemRequest.objects.filter(
        status='issued',
        item__needs_maintenance=True
    ).select_related('item', 'user')

    if search_query:
        issued_requests = issued_requests.filter(
            Q(item__name__icontains=search_query) |
            Q(item__serial_number__icontains=search_query)
        )

    today = timezone.now().date()
    filtered_items = []

    for req in issued_requests:
        item = req.item
        interval = item.maintenance_interval_days

        # Fallback to issued_date only if last_maintenance is missing
        last_maint_date = item.last_maintenance_date or (req.issued_date.date() if req.issued_date else None)
        
        # If no dates at all, skip item from filtering as it's invalid
        if not last_maint_date or not interval:
            if not filter_value:  # Include only in unfiltered case
                filtered_items.append(req)
            continue

        days_since = (today - last_maint_date).days
        is_overdue = days_since > interval

        if filter_value == 'overdue' and is_overdue:
            filtered_items.append(req)
        elif filter_value == 'due' and not is_overdue:
            filtered_items.append(req)
        elif not filter_value:
            filtered_items.append(req)

    # Paginate results
    paginator = Paginator(filtered_items, 30)
    page_obj = paginator.get_page(request.GET.get('items_page'))
    user_requested_maintenance = MaintenanceRequest.objects.filter(status = 'pending')

    return render(request, 'maintenance/maintenance_page.html', {
        'maintenance_items': page_obj,
        'user_requested_maintenance':user_requested_maintenance
    })


# -------------------- Clerk: Mark Item as Maintained --------------------
from django.db import transaction

@login_required
@user_passes_test(is_clerk)
def mark_maintained(request, item_id):

    try:
        with transaction.atomic():
            item_request = get_object_or_404(ItemRequest, id=item_id)
            inventory_item = item_request.item
            inventory_item.last_maintenance_date = timezone.now().date()
            inventory_item.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_clerk)
def request_mark_maintained(request, item_id):
    try:
        with transaction.atomic():
            item_maintenance_request = get_object_or_404(MaintenanceRequest, id=item_id)
            inventory_item = getattr(item_maintenance_request, 'item', None)
            if not inventory_item:
                raise ValueError("The associated inventory item could not be found.")
            
            item_maintenance_request.status = 'completed'
            item_maintenance_request.completion_date = timezone.now().date()
            item_maintenance_request.resolved_by = request.user
            inventory_item.last_maintenance_date = timezone.now().date()
            
            if hasattr(inventory_item, 'issued_to') and inventory_item.issued_to:
                inventory_item.status = 'issued'
            else:
                inventory_item.status = 'available'
            
            item_maintenance_request.save()
            inventory_item.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# -------------------- Faculty View: My Maintenance Items --------------------

@login_required
def user_item_maintenance(request):
    search_query = request.GET.get('q', '')
    filter_value = request.GET.get('filter', '')

    user_requests = ItemRequest.objects.filter(
        user=request.user,
        status='issued',
        item__needs_maintenance=True
    ).select_related('item')

    if search_query:
        user_requests = user_requests.filter(
            Q(item__name__icontains=search_query) |
            Q(item__serial_number__icontains=search_query)
        )

    today = timezone.now().date()
    filtered_items = []

    for req in user_requests:
        item = req.item
        due_interval = item.maintenance_interval_days

        # Get last maintenance date (fallback to issued date)
        last_maintenance_date = item.last_maintenance_date or req.issued_date.date()
        if isinstance(last_maintenance_date, datetime.datetime):
            last_maintenance_date = last_maintenance_date.date()

        days_since_maintenance = (today - last_maintenance_date).days
        is_overdue = due_interval and days_since_maintenance > due_interval

        if filter_value == 'overdue' and is_overdue:
            filtered_items.append(req)
        elif filter_value == 'due' and not is_overdue:
            filtered_items.append(req)
        elif not filter_value:
            filtered_items.append(req)

    paginator = Paginator(filtered_items, 30)
    page_obj = paginator.get_page(request.GET.get('items_page'))


    return render(request, 'maintenance/maintenance_page.html', {
        'maintenance_items': page_obj,
    })


from django.utils.timezone import now  # Ensure 'now' is imported

@login_required
def request_maintenance(request, item_id):
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages

    if request.method == 'POST':
        issue_description = request.POST.get('issue_description', '').strip()
        if not issue_description:
            # Redirect on missing issue description with a message
            messages.error(request, "Issue description is required.")
            return redirect('your_issued_items', id = request.user.id)

        try:
            inventory_item = get_object_or_404(InventoryItem, id=item_id, issued_to=request.user)
            MaintenanceRequest.objects.create(
                item=inventory_item,
                reported_by=request.user,
                issue_description=issue_description,
                reported_on=now()
            )
            inventory_item.status = 'maintenance'
            inventory_item.save()
            # Redirect after successful maintenance request with a success message
            messages.success(request, "Maintenance request submitted successfully.")
            return redirect('your_issued_items', id = request.user.id )
        
        except Exception:
            # Redirect on error with an error message
            messages.error(request, "An error occurred while submitting the maintenance request.")
            return redirect('your_issued_items', id = request.user.id)

    # GET request — render the maintenance form
    item = get_object_or_404(InventoryItem, id=item_id, issued_to=request.user)
    return render(request, 'maintenance/request_maintenance.html', {'item': item})

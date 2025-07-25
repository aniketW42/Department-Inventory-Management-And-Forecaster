from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import InventoryItem, ItemRequest, ItemGroup, MaintenanceRequest
from .forms import InventoryItemForm
from .utils import is_clerk

User = get_user_model()


# --------------------- View All Inventory Items ---------------------

from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from .models import InventoryItem, ItemGroup

@login_required
def show_all_items(request):
    # Get filter parameters from GET
    search_query = request.GET.get('q', '').strip()
    group_id = request.GET.get('group', '')
    status = request.GET.get('status', 'available')
    item_type = request.GET.get('item_type', '')
    category = request.GET.get('category', '')
    items = InventoryItem.objects.all().order_by('-date_added')

    # ---- Filtering ----
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) | 
            Q(serial_number__icontains=search_query) | 
            Q(asset_tag__icontains=search_query)
        )

    if group_id:
        items = items.filter(item_group_id=group_id)
    if status:
        items = items.filter(status=status)
    if item_type:
        items = items.filter(item_type=item_type)
    if category:
        items = items.filter(category=category)

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Status counts (for possible dashboard)
    in_stock_items = items.filter(status='available').count()
    low_stock_items = items.filter(status='available', category='stationery').count()   
    out_of_stock_items = items.exclude(status='available').count()
    stock_info = {
        'in_stock': in_stock_items,
        'low_stock': low_stock_items,
        'out_stock': out_of_stock_items,
    }

    # For filter dropdowns
    categories = InventoryItem.CATEGORY_CHOICES
    item_types = InventoryItem.ITEM_TYPE_CHOICES
    statuses = InventoryItem.STATUS_CHOICES
    groups = ItemGroup.objects.all()

    context = {
        'items': page_obj,
        'stock_info': stock_info,
        'categories': categories,
        'item_types': item_types,
        'statuses': statuses,
        'groups': groups,
        'filter_params': request.GET,  # to prefill filter fields
    }
    return render(request, 'inventory/show_all_items.html', context)

# item views


@login_required
def item_detail(request, item_id):
    """
    Display comprehensive details for a single inventory item.
    """
    item = get_object_or_404(InventoryItem, id=item_id)
    
    # Get related requests
    item_requests = ItemRequest.objects.filter(item=item).select_related('user', 'processed_by').order_by('-request_date')
    
    # Get maintenance history
    maintenance_history = MaintenanceRequest.objects.filter(item=item).select_related('reported_by', 'resolved_by').order_by('-reported_on')
    
    # Calculate days since last maintenance
    days_since_maintenance = None
    if item.last_maintenance_date:
        from datetime import date
        days_since_maintenance = (date.today() - item.last_maintenance_date).days
    
    # Check if maintenance is due
    maintenance_due = False
    if item.needs_maintenance and item.maintenance_interval_days and days_since_maintenance:
        maintenance_due = days_since_maintenance >= item.maintenance_interval_days
    
    # Get current request (if issued)
    current_request = None
    if item.status == 'issued':
        current_request = item_requests.filter(status='issued').first()
    
    user_requested_items = ItemRequest.objects.filter(status='pending', user=request.user).values_list('item', flat=True)
    context = {
        'item': item,
        'item_requests': item_requests,
        'maintenance_history': maintenance_history,
        'days_since_maintenance': days_since_maintenance,
        'maintenance_due': maintenance_due,
        'current_request': current_request,
        'request_count': item_requests.count(),
        'maintenance_count': maintenance_history.count(),
        'user_requested_items': user_requested_items
    }
    
    return render(request, 'inventory/item_detail.html', context)

# --------------------- Clerk: Delete an Inventory Item ---------------------

@login_required
@require_POST
@user_passes_test(is_clerk)
def delete_item(request, pk):
    try:
        item = InventoryItem.objects.get(pk=pk)

        # Prevent deletion if issued or in use
        if item.status in ['issued', 'maintenance']:
            return JsonResponse({'success': False, 'error': 'Cannot delete an item that is issued or under maintenance.'})

        item.delete()
        return JsonResponse({'success': True})
    except InventoryItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


# --------------------- Clerk: Add New Inventory Item ---------------------

# @login_required
# @user_passes_test(is_clerk)
# def add_item(request):
#     if request.method == 'POST':
#         form = InventoryItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             item = form.save(commit=False)
#             item.added_by = request.user
#             item.save()
#             messages.success(request, "Item added successfully.")
#             return redirect('add_item')
#         else:
#             messages.error(request, "There was a problem adding the item.")
#     else:
#         form = InventoryItemForm()
#     return render(request, 'inventory/add_edit_item.html', {'form': form})
@login_required
@user_passes_test(is_clerk)
def add_item(request):
    if request.method == 'POST':
        # 1. Check: Did the user request to create a new group?
        new_group_name = request.POST.get('new_group_name', '').strip()
        item_group_instance = None

        if new_group_name:
            # User wants to create a new ItemGroup
            item_group_instance, created = ItemGroup.objects.get_or_create(
                name=new_group_name,
                defaults={
                    'category': request.POST.get('new_group_category', '').strip(),
                    'description': request.POST.get('new_group_description', '').strip(),
                    'reorder_level': request.POST.get('new_group_reorder')
                }
            )

        # 2. Create form. As item_group is a ModelChoiceField, we have to fill it in if using a new group:
        data = request.POST.copy()
        files = request.FILES

        if item_group_instance:
            data['item_group'] = item_group_instance.pk  # Set PK so ModelForm validates!

        form = InventoryItemForm(data, files)

        if form.is_valid():
            item = form.save(commit=False)
            item.added_by = request.user
            # If a new group, ensure model instance has the actual FK, in case model field isn't required:
            if item_group_instance:
                item.item_group = item_group_instance
            item.save()
            messages.success(request, "Item added successfully.")
            return redirect('add_item')
        else:
            messages.error(request, "There was a problem adding the item.")
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/add_edit_item.html', {'form': form})


# --------------------- Clerk: Edit Existing Item ---------------------

@login_required
@user_passes_test(is_clerk)
def edit_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if request.method == 'POST':
        form = InventoryItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.modified_by = request.user
            item.save()
            messages.success(request, "Item updated successfully.")
            return redirect('inventory_items')
        else:
            messages.error(request, "Error updating item.")
    else:
        form = InventoryItemForm(instance=item)

    return render(request, 'inventory/add_edit_item.html', {'form': form, 'item': item})


# --------------------- View Items Issued to a Specific User ---------------------

@login_required
def view_issued_items(request, id):
    # Get only requests that are currently issued (status='issued')
    requests = ItemRequest.objects.filter(user__id=id, status__in=['issued', 'return_requested']).select_related('item')

    user = get_object_or_404(User, id=id)

    paginator = Paginator(requests, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # under_maintenance = MaintenanceRequest.objects.filter(user__id=id)

    return render(request, 'user/view_issued_items.html', {
        'requser': user,
        'requests': page_obj
    })

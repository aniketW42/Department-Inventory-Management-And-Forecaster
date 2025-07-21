from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import InventoryItem, ItemRequest, MaintenanceRequest
from .forms import InventoryItemForm
from .utils import is_clerk

User = get_user_model()


# --------------------- View All Inventory Items ---------------------

@login_required
def show_all_items(request):
    items = InventoryItem.objects.filter(status='available').order_by('-date_added')

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Updated: status-based stock counts (instead of quantity)
    in_stock_items = items.filter(status='available').count()
    low_stock_items = items.filter(status='available', category='stationery').count()  
    out_of_stock_items = items.exclude(status='available').count()

    stock_info = {
        'in_stock': in_stock_items,
        'low_stock': low_stock_items,
        'out_stock': out_of_stock_items,
    }

    categories = InventoryItem.CATEGORY_CHOICES
    return render(request, 'inventory/show_all_items.html', {
        'items': page_obj,
        'stock_info': stock_info,
        'categories': categories,
    })


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

@login_required
@user_passes_test(is_clerk)
def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.added_by = request.user
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

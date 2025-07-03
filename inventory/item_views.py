from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from .models import InventoryItem, ItemRequest
from .forms import InventoryItemForm
from .utils import is_clerk
from django.contrib.auth.models import User
@login_required
def show_all_items(request):
    # Get base queryset
    items = InventoryItem.objects.all()
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(
            name__icontains=search_query
        ) | items.filter(
            description__icontains=search_query
        )
    
    # Apply category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        items = items.filter(category=category_filter)
    
    # Apply stock status filter
    stock_status = request.GET.get('stock_status', '')
    if stock_status == 'in_stock':
        items = items.filter(quantity__gt=10)
    elif stock_status == 'low_stock':
        items = items.filter(quantity__gt=0, quantity__lte=10)
    elif stock_status == 'out_of_stock':
        items = items.filter(quantity=0)
    
    # Calculate statistics for all items (not filtered)
    all_items = InventoryItem.objects.all()
    total_items = all_items.count()
    in_stock_count = all_items.filter(quantity__gt=10).count()
    low_stock_count = all_items.filter(quantity__gt=0, quantity__lte=10).count()
    out_of_stock_count = all_items.filter(quantity=0).count()
    
    # Order items
    items = items.order_by('-date_added')
    
    # Pagination
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = InventoryItem.CATEGORY_CHOICES
    
    context = {
        'items': page_obj,
        'total_items': total_items,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_filter,
        'current_stock_status': stock_status,
    }
    
    return render(request, 'inventory/show_all_items.html', context)

@login_required
@require_POST
@user_passes_test(is_clerk)
def delete_item(request, pk):
    try:
        item = InventoryItem.objects.get(pk=pk)
        item.delete()
        return JsonResponse({'success': True})
    except InventoryItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

@login_required
@user_passes_test(is_clerk)
def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully.")
            return redirect('add_item')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/add_edit_item.html', {'form': form})

@login_required
@user_passes_test(is_clerk)
def edit_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully.")
            return redirect('inventory_items')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory/add_edit_item.html', {'form': form, 'item': item})

# from django.db.models import Count
@login_required
def view_issued_items(request, id):

    requests = ItemRequest.objects.filter(user__id = id, status = 'issued')
    user = User.objects.filter(id=id).first
    paginator = Paginator(requests, 20) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user/view_issued_items.html' , {'requser':user, 'requests':page_obj})

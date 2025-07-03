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
    items = InventoryItem.objects.all()

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    in_stock_items = items.filter(quantity__gte=5).count()   # Only items with good stock
    low_stock_items = items.filter(quantity__gt=0, quantity__lt=10).count()
    out_of_stock_items = items.filter(quantity=0).count()

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

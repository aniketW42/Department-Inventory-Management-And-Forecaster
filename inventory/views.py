from .utils import is_clerk, is_faculty, is_hod
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ItemRequest, InventoryItem
from .forms import ItemRequestForm
from django.contrib.auth import login ,logout, authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .utils import forecast_usage_from_excel
import os

def home(request):
    if is_clerk(request.user):
        return redirect('clerk_dashboard')
    elif is_faculty(request.user):
        return redirect('faculty_dashboard')
    elif is_hod(request.user):
        return redirect('hod_dashboard')
    else:
        return render(request, 'base.html')  

@login_required
def request_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)

    if request.method == 'POST':
        form = ItemRequestForm(request.POST)
        if form.is_valid():
            item_request = form.save(commit=False)
            item_request.user = request.user
            item_request.item = item  # set the item manually
            item_request.status = 'pending'
            item_request.save()
            return redirect('faculty_dashboard')
    else:
        form = ItemRequestForm(initial={'item': item})

    return render(request, 'requests/request_item.html', {'form': form, 'item': item})

def logout_page(request):
    logout(request)
    return redirect('home')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, 'Invalid Credentials')
    
    return render(request, 'user/login.html')

@login_required
def view_requests(request):
    requests = ItemRequest.objects.all().order_by('-request_date')
    return render(request, 'requests/view_requests.html', {'requests': requests})

# @staff_member_required
def manage_requests(request):
    requests = ItemRequest.objects.all().order_by('-request_date')
    return render(request, 'inventory/manage_requests.html', {'requests': requests})

@user_passes_test(is_hod)
@require_POST
def process_request(request, request_id):
    item_request = get_object_or_404(ItemRequest, id=request_id)
    action = request.POST.get('action')

    if item_request.status != 'pending':
        messages.warning(request, "This request has already been processed.")
        return redirect('hod_dashboard')

    if action == 'approve':
        item = item_request.item
        if item.quantity >= item_request.quantity:
            item.quantity -= item_request.quantity
            item.save()

            item_request.status = 'approved'
            item_request.processed_by = request.user
            item_request.save()

            messages.success(request, "Request approved and inventory updated.")
        else:
            messages.error(request, "Not enough stock to approve this request.")
            return redirect('hod_dashboard')

    elif action == 'reject':
        item_request.status = 'rejected'
        item_request.processed_by = request.user
        item_request.save()

        messages.info(request, "Request has been rejected.")

    else:
        messages.error(request, "Invalid action.")
    
    return redirect('hod_dashboard')


@login_required
def request_history(request):
    if is_faculty(request.user):
        requests = ItemRequest.objects.filter(user=request.user).order_by('-request_date')
    else:  # Clerk or HOD
        requests = ItemRequest.objects.all().order_by('-request_date')
    
    return render(request, 'requests/request_history.html', {'requests': requests})

from django.contrib.auth.decorators import login_required
from inventory.models import InventoryItem, ItemRequest
from django.db.models import Count, Q

@login_required
def clerk_dashboard(request):
    total_items = InventoryItem.objects.count()
    low_stock_items = InventoryItem.objects.filter(quantity__lt=5).count()  # Adjust threshold
    pending_requests = ItemRequest.objects.filter(user=request.user, status='pending').count()
    issued_items = ItemRequest.objects.filter(user=request.user, status='issued').count()

    recent_requests = ItemRequest.objects.filter(user=request.user).order_by('-request_date')[:5]

    context = {
        'total_items': total_items,
        'low_stock': low_stock_items,
        'pending_requests': pending_requests,
        'issued_items': issued_items,
        'recent_requests': recent_requests,
    }
    return render(request, 'dashboard/clerk_dashboard.html', context)

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def hod_dashboard(request):
    total_requests = ItemRequest.objects.count()
    pending_requests = ItemRequest.objects.filter(status='pending').count()
    approved_requests = ItemRequest.objects.filter(status='approved').count()
    rejected_requests = ItemRequest.objects.filter(status='rejected').count()

    recent_requests = ItemRequest.objects.all().order_by('-request_date')[:5]

    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'recent_requests': recent_requests,
    }
    return render(request, 'dashboard/hod_dashboard.html', context)

from django.contrib.auth.decorators import login_required
from inventory.models import InventoryItem, ItemRequest

@login_required
def faculty_dashboard(request):
    items = InventoryItem.objects.all()
    my_requests = ItemRequest.objects.filter(user=request.user).order_by('-request_date')
    return render(request, 'dashboard/faculty_dashboard.html', {
        'items': items,
        'my_requests': my_requests
    })

from django.views.decorators.http import require_POST

@login_required
@user_passes_test(is_clerk)
def issue_items(request):
    approved_requests = ItemRequest.objects.filter(status='approved').order_by('-request_date')
    return render(request, 'requests/issue_items.html', {'approved_requests': approved_requests})

@login_required
@user_passes_test(is_clerk)
@require_POST
def mark_as_issued(request, request_id):
    item_request = get_object_or_404(ItemRequest, id=request_id, status='Approved')

    item_request.status = 'Issued'
    item_request.save()
    messages.success(request, "Item marked as issued.")
    return redirect('issue_items')  # URL name for issue_items view


@login_required
def show_all_items(request):
    items = InventoryItem.objects.all()
    return render(request, 'inventory/show_all_items.html', {'items': items})

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import InventoryItem

@require_POST
def delete_item(request, pk):
    try:
        item = InventoryItem.objects.get(pk=pk)
        item.delete()
        return JsonResponse({'success': True})
    except InventoryItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

from .forms import InventoryItemForm

def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully.")
            return redirect('inventory_items')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/add_item.html', {'form': form})


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
    return render(request, 'inventory/edit_item.html', {'form': form, 'item': item})



def predict_usage(request):
    forecast_data = {}
    forecast_year = 2025  # You can later make this dynamic from a form

    excel_path = os.path.join('media', 'stationery_usage.xlsx')  # Make sure file exists
    try:
        forecast_data = forecast_usage_from_excel(excel_path, forecast_year)
    except Exception as e:
        forecast_data = {'error': str(e)}

    return render(request, 'predict_usage.html', {
        'forecast_data': forecast_data,
        'forecast_year': forecast_year
    })

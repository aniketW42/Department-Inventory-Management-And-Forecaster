from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import InventoryItem, ItemRequest
from .utils import is_clerk, is_faculty, is_hod

User = get_user_model()


# --------------------- Home Redirect ---------------------

def home(request):
    if is_clerk(request.user):
        return redirect('clerk_dashboard')
    elif is_faculty(request.user):
        return redirect('faculty_dashboard')
    elif is_hod(request.user):
        return redirect('hod_dashboard')
    else:
        return redirect('login')


# --------------------- Clerk Dashboard ---------------------

@login_required
@user_passes_test(is_clerk)
def clerk_dashboard(request):
    recent_requests = ItemRequest.objects.all().order_by('-request_date')
    recent_approved_requests = ItemRequest.objects.filter(status='approved').order_by('-request_date')
    pending_requests = ItemRequest.objects.filter(status='pending').count()
    approved_requests = ItemRequest.objects.filter(status='approved').count()
    context = {
        'recent_requests': recent_requests,
        'all_pending_requests': pending_requests,
        'all_approved_requests': approved_requests,
        'recent_approved_requests': recent_approved_requests
    }
    return render(request, 'dashboard/clerk_dashboard.html', context)


# --------------------- HOD Dashboard ---------------------

@staff_member_required
@user_passes_test(is_hod)
def hod_dashboard(request):
    total_requests = ItemRequest.objects.count()
    pending_requests = ItemRequest.objects.filter(status='pending').count()
    approved_requests = ItemRequest.objects.filter(status='approved').count()
    rejected_requests = ItemRequest.objects.filter(status='rejected').count()
    issued_requests = ItemRequest.objects.filter(status='issued').count()
    returned_requests = ItemRequest.objects.filter(status='returned').count()
    recent_requests = ItemRequest.objects.all().order_by('-request_date')

    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'issued_requests': issued_requests,
        'returned_requests': returned_requests,
        'recent_requests': recent_requests,
    }
    return render(request, 'dashboard/hod_dashboard.html', context)


# --------------------- Faculty Dashboard ---------------------

@login_required
@user_passes_test(is_faculty)
def faculty_dashboard(request):
    # Only show items that are available
    items = InventoryItem.objects.filter(status='available')
    my_requests = ItemRequest.objects.filter(user=request.user).order_by('-request_date')

    items_paginator = Paginator(items, 50)
    items_page = items_paginator.get_page(request.GET.get('items_page'))

    requests_paginator = Paginator(my_requests, 100)
    requests_page = requests_paginator.get_page(request.GET.get('requests_page'))

    return render(request, 'dashboard/faculty_dashboard.html', {
        'items': items_page,
        'my_requests': requests_page
    })


# --------------------- Clerk - View Approved Requests ---------------------

@login_required
@user_passes_test(is_clerk)
def issue_items(request):
    approved_requests = ItemRequest.objects.filter(status='approved').select_related('item').order_by('-request_date')
    return render(request, 'requests/issue_items.html', {'approved_requests': approved_requests})


# --------------------- Clerk - Mark As Issued ---------------------

@login_required
@user_passes_test(is_clerk)
@require_POST
def mark_as_issued(request, request_id):
    try:
        with transaction.atomic():
            item_request = get_object_or_404(ItemRequest, id=request_id, status='approved')
            item = item_request.item

            # Check if item is actually available
            if item.status != 'available':
                messages.error(request, "Item is not available to be issued.")
                return redirect('/clerk-dashboard/?view=approved')

            item.status = 'issued'
            item.issued_to = item_request.user
            item.last_maintenance_date = timezone.now()
            item.save()

            item_request.status = 'issued'
            item_request.issued_date = timezone.now()
            item_request.issued_by = request.user
            item_request.decision_date = timezone.now()
            item_request.save()

            messages.success(request, f"Item '{item.name}' issued successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('/clerk-dashboard/?view=approved')


# --------------------- NEW: Clerk - Mark as Returned ---------------------

@login_required
@user_passes_test(is_clerk)
@require_POST
def mark_as_returned(request, request_id):
    try:
        with transaction.atomic():
            item_request = get_object_or_404(ItemRequest, id=request_id, status='return_requested')
            item = item_request.item

            item.status = 'available'
            item.issued_to = None
            item.save()

            item_request.status = 'returned'
            item_request.return_date = timezone.now()
            item_request.save()

            messages.success(request, f"Item '{item.name}' returned successfully.")
    except Exception as e:
        messages.error(request, f"Failed to mark as returned: {str(e)}")

    return redirect('view_return_requests')


# --------------------- HOD - Manage Users ---------------------

@login_required
@user_passes_test(is_hod)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'user/manage_users.html', {'users': users})

@login_required
@user_passes_test(is_clerk)
def return_requests_clerk(request):
    return_requests = ItemRequest.objects.select_related('item', 'user').filter(status='return_requested')
    return render(request, 'inventory/clerk_return_requests.html', {'requests': return_requests})
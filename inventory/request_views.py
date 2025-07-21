from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator

from .models import InventoryItem, ItemRequest
from .utils import is_faculty, is_hod, is_clerk
from notifications.utils import notify_user


# --------------------- Faculty - Request Item Page ---------------------

@login_required
def request_item_page(request):
    # Show only available and unissued items (non-maintenance)

    items = InventoryItem.objects.filter(status='available')
    user_requested_items = ItemRequest.objects.filter(status='pending', user=request.user).values_list('item', flat=True)
    return render(request, 'requests/request_item.html', {'items': items, 'user_requested_items':user_requested_items})


# --------------------- Faculty - Submit Item Request ---------------------

@login_required
def submit_item_request(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        reason = request.POST.get('reason')

        # Fetch the requested item
        item = get_object_or_404(InventoryItem, id=item_id)

        # Check if item is available before request
        if item.status != 'available':
            messages.error(request, "Item is no longer available.")
            return redirect('request_item_page')

        # Create request for specific instance
        ItemRequest.objects.create(
            user=request.user,
            item=item,
            reason=reason,
            status='pending',
            request_date=timezone.now()
        )

        # Notify HOD about the request
        hod_group = Group.objects.get(name='HOD')
        for hod in hod_group.user_set.all():
            notify_user(hod, f"{request.user.username} requested item '{item.name}'.")

        messages.success(request, "Item requested successfully.")
        return redirect('request_item')
    
    return HttpResponseBadRequest("Invalid request method.")


# --------------------- View Request History (Faculty or Staff) ---------------------

@login_required
def request_history(request):

    if is_faculty(request.user):
        all_requests = ItemRequest.objects.filter(user=request.user).order_by('-request_date')
    else:
        total_requests = ItemRequest.objects.count()
        pending_requests = ItemRequest.objects.filter(status='pending').count()
        approved_requests = ItemRequest.objects.filter(status='approved').count()
        rejected_requests = ItemRequest.objects.filter(status='rejected').count()
        issued_requests = ItemRequest.objects.filter(status='issued').count()
        returned_requests = ItemRequest.objects.filter(status='returned').count()
        all_requests = ItemRequest.objects.all().order_by('-request_date')

    paginator = Paginator(all_requests, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'requests/request_history.html', {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'issued_requests': issued_requests,
        'returned_requests': returned_requests,
        'requests': page_obj,
    })


# --------------------- HOD/Clerk - View All Requests ---------------------

@login_required
def view_all_requests(request):
    requests = ItemRequest.objects.all().order_by('-request_date')
    return render(request, 'requests/view_requests.html', {'requests': requests})


@login_required
def view_requests(request, user_id):
    user = get_object_or_404(User, id=user_id)
    requests = ItemRequest.objects.filter(user__id=user_id).order_by('-request_date')

    paginator = Paginator(requests, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'requests/view_requests.html', {'requser': user, 'requests': page_obj})


# --------------------- HOD/Clerk - Manage All Requests ---------------------

@user_passes_test(is_hod or is_clerk)
def manage_requests(request):
    requests = ItemRequest.objects.all().order_by('-request_date')
    return render(request, 'inventory/manage_requests.html', {'requests': requests})


# --------------------- HOD - Approve or Reject Request ---------------------

@user_passes_test(is_hod)
@require_POST
def process_request(request, request_id):
    item_request = get_object_or_404(ItemRequest, id=request_id)

    if item_request.status != 'pending':
        messages.warning(request, "This request has already been processed.")
        return redirect('hod_dashboard')

    action = request.POST.get('action')
    item = item_request.item

    if action == 'approve':
        if item.status == 'available':
            try:
                item_request.status = 'approved'
                item_request.processed_by = request.user
                item_request.decision_date = timezone.now()
                item_request.save()
                # Notifications
                notify_user(item_request.user, f"Your request for '{item.name}' has been approved by {request.user.username}.")
                
                clerk_group = Group.objects.get(name='Clerk')
                for clerk in clerk_group.user_set.all():
                    notify_user(clerk, f"{item_request.user.username}'s request for '{item.name}' was approved by {request.user.username}.")

                messages.success(request, "Request approved successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, f"The item '{item.name}' is no longer available.")

    elif action == 'reject':
        item_request.status = 'rejected'
        item_request.processed_by = request.user
        item_request.decision_date = timezone.now()
        item_request.save()

        notify_user(item_request.user, f"Your request for '{item.name}' has been rejected by {request.user.username}.")
        messages.info(request, "Request rejected.")

    else:
        messages.error(request, "Invalid action.")

    return redirect('/hod-dashboard/?view=pending')


# Staff triggers return request
@login_required
def return_item_request(request, request_id):
    req = get_object_or_404(ItemRequest, id=request_id, user=request.user, status='issued')
    req.status = 'return_requested'
    req.save()
    messages.success(request, f"Return request submitted for item: {req.item.name}")
    from django.urls import reverse
    return redirect(reverse('your_issued_items', kwargs={'id': request.user.id}))

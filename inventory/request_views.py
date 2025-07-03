from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.utils.timezone import datetime
from django.contrib.auth.models import Group
from .models import InventoryItem, ItemRequest
from .utils import is_faculty, is_hod, is_clerk
from notifications.utils import notify_user
from django.core.paginator import Paginator
from django.contrib.auth.models import User

@login_required
def request_item_page(request):
    items = InventoryItem.objects.filter(quantity__gt=0)
    return render(request, 'requests/request_item.html', {'items': items})

@login_required
def request_history(request):
    if is_faculty(request.user):
        all_requests = ItemRequest.objects.filter(user=request.user).order_by('-request_date')
    else:
        all_requests = ItemRequest.objects.all().order_by('-request_date')

    paginator = Paginator(all_requests, 20)  # Show 10 requests per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'requests/request_history.html', {
        'requests': page_obj,
    })


@login_required
def view_all_requests(request):
    requests = ItemRequest.objects.all().order_by('-request_date')
    return render(request, 'requests/view_requests.html', {'requests': requests})

@login_required
def view_requests(request, user_id):
    requests = ItemRequest.objects.filter( user__id = user_id )
   
    user = User.objects.filter(id = user_id).first
    paginator = Paginator(requests, 20)  # Show 10 requests per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'requests/view_requests.html', {'requser':user, 'requests': page_obj})

@user_passes_test(is_hod or is_clerk)
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
            item_request.decision_date = datetime.now()
            item_request.save()
            notify_user(item_request.user, f"Your request for {item.name} has been approved by {request.user}.")
            clerk_group = Group.objects.get(name='Clerk')
            for clerk in clerk_group.user_set.all():
                notify_user(clerk, f" {item_request.user}'s request for {item.name} has been approved by {request.user}.")
            messages.success(request, "Request approved and inventory updated.")
        else:
            messages.error(request, "Not enough stock to approve this request.")
            return redirect('hod_dashboard')

    elif action == 'reject':
        item_request.status = 'rejected'
        item_request.processed_by = request.user
        item_request.save()
        notify_user(item_request.user, f"Your request for {item.item.name} has been rejected.")
        messages.info(request, "Request has been rejected.")

    else:
        messages.error(request, "Invalid action.")
    
    return redirect('hod_dashboard')

@login_required
def submit_item_request(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')
        item = get_object_or_404(InventoryItem, id=item_id)

        ItemRequest.objects.create(
            user=request.user,
            item=item,
            quantity=quantity,
            reason=reason,
            status='pending',
            request_date = datetime.now()
        )
        hod_group = Group.objects.get(name='HOD')
        for hod in hod_group.user_set.all():
            notify_user(hod, f"{request.user.username} requested {item.name} of quantity {quantity}.")
        messages.success(request, 'Request submitted successfully.')
        return redirect('home')
    return HttpResponseBadRequest("Invalid request.")
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notification_list')

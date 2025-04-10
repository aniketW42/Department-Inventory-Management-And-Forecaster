from .models import Notification

def notify_user(user, message):
    Notification.objects.create(user=user, message=message)

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']

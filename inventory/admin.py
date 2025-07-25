from django.contrib import admin
from .models import ItemGroup, InventoryItem, ItemRequest, MaintenanceRequest
from django.utils.dateformat import format

admin.site.register(ItemGroup)
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'name','item_group', 'category', 'item_type', 'status', 'date_added']
    list_filter = ['category', 'item_type', 'status']
    search_fields = ['serial_number', 'name', 'asset_tag', 'location']

@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ['item', 'user', 'status', 'request_date', 'get_last_maintenance_date']
    list_filter = ['status', 'priority']
    search_fields = ['item__name', 'item__serial_number', 'user__username']
    @admin.display(description='Last Maintenance Date')
    def get_last_maintenance_date(self, obj):
        if obj.item.last_maintenance_date:
            return format(obj.item.last_maintenance_date, 'Y-m-d')
        return '—'
    
@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['item', 'reported_by', 'status', 'reported_on', 'completion_date']
    list_filter = ['status']
    search_fields = ['item__serial_number', 'reported_by__username']

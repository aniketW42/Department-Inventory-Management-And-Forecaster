from django.contrib import admin
from .models import InventoryItem, ItemRequest, MaintenanceRequest
# Register your models here.
admin.site.register(InventoryItem)
# admin.site.register(ItemRequest)
@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'status', 'request_date', 'last_maintenance_date']
admin.site.register(MaintenanceRequest)

# @admin.register(InventoryItem)
# class InventoryItemAdmin(admin.ModelAdmin):
#     list_display = ('name', 'item_type', 'quantity', 'location', 'reorder_level')
#     search_fields = ('name', 'category', 'location')

# @admin.register(ItemRequest)
# class ItemRequestAdmin(admin.ModelAdmin):
#     list_display = ('user', 'item', 'quantity', 'status', 'request_date')
#     list_filter = ('status',)
#     search_fields = ('user__username', 'item__name')

# @admin.register(MaintenanceRequest)
# class MaintenanceRequestAdmin(admin.ModelAdmin):
#     list_display = ('item', 'reported_by', 'status', 'reported_on')
#     list_filter = ('status',)
#     search_fields = ('item__name', 'reported_by__username')
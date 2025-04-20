from django.db import models
from django.contrib.auth.models import User

class InventoryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('consumable', 'Consumable'),
        ('non-consumable', 'Non-Consumable'),
    ]
    CATEGORY_CHOICES = [
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('stationery', 'Stationery'),
        ('tools', 'Tools'),
        ('cleaning_supplies', 'Cleaning Supplies'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True)
    location = models.CharField(max_length=100, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ItemRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('issued', 'Issued'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=False)
    decision_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="processor")
    def __str__(self):
        return f"{self.user.username} - {self.item.name} - {self.request_date.month},{self.request_date.year} ({self.status})"

class MaintenanceRequest(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    reported_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='pending')
    reported_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name} - {self.status}"

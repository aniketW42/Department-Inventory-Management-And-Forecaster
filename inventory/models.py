from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
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
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    location = models.CharField(max_length=100, blank=True)
    reorder_level = models.PositiveIntegerField(default=5)
    date_added = models.DateTimeField(auto_now_add=True)

    needs_maintenance = models.BooleanField(default=False)
    maintenance_interval_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of days after which maintenance is needed (if applicable)"
    )
    def clean(self):
        if self.needs_maintenance and not self.maintenance_interval_days:
            raise ValidationError("Maintenance interval days must be set if the item needs maintenance.")
        if self.needs_maintenance and self.maintenance_interval_days <= 0:
            raise ValidationError("Maintenance interval days must be a positive integer.")
        

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['item_type']),
            models.Index(fields=['category']),
        ]

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
    request_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="processor")
    issued_date = models.DateTimeField(null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="issuer")
    last_maintenance_date = models.DateField(null=True, blank=True)

    def clean(self):
        if self.quantity > self.item.quantity:
            raise ValidationError("Requested quantity exceeds available inventory.")
        if self.status == 'issued':
            if not self.issued_date or not self.issued_by:
                raise ValidationError("Issued date and issuer must be set when item is marked as issued.")
            if self.issued_date and self.issued_date > timezone.now():
                raise ValidationError("Issued date cannot be in the future.")
            if self.decision_date and self.issued_date and self.issued_date < self.decision_date:
                raise ValidationError("Issued date cannot be before decision date.")
        if self.status == 'returned':
            if not self.return_date:
                raise ValidationError("Return date must be set when item is returned.")
            if self.return_date and self.return_date > timezone.now():
                raise ValidationError("Return date cannot be in the future.")
            if self.issued_date and self.return_date and self.return_date < self.issued_date:
                raise ValidationError("Return date cannot be before issued date.")
        if self.decision_date and self.decision_date > timezone.now():
            raise ValidationError("Decision date cannot be in the future.")
        if self.last_maintenance_date and self.last_maintenance_date > timezone.now().date():
            raise ValidationError("Last maintenance date cannot be in the future.")
        if self.last_maintenance_date and self.status != "issued":
            raise ValidationError("Cannot set last maintenance date unless item is marked as issued.")


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.item.name} - {self.request_date.month},{self.request_date.year} ({self.status})"

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['request_date']),
        ]

class MaintenanceRequest(models.Model): # each issued item will have its separate maintenece record
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

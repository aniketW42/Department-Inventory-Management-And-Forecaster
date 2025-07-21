from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


# ------------------------ Inventory Item ------------------------

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

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('issued', 'Issued'),
        ('maintenance', 'Under Maintenance'),
        ('damaged', 'Damaged'),
        ('retired', 'Retired'),
    ]

    serial_number = models.CharField(
        max_length=120,
        unique=True,
        null=True,          # ✅ Allow null temporarily
        blank=True          # ✅ Allow admin form to skip validation
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='other')
    location = models.CharField(max_length=100, blank=True, help_text="E.g. Lab A, Room 103")

    asset_tag = models.CharField(max_length=100, blank=True, null=True, unique=True)
    reorder_level = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    date_added = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)

    needs_maintenance = models.BooleanField(default=False)
    maintenance_interval_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of days between maintenance"
    )
    last_maintenance_date = models.DateField(null=True, blank=True)

    issued_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_items')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_added')
    modified_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.needs_maintenance and (not self.maintenance_interval_days or self.maintenance_interval_days <= 0):
            raise ValidationError("Maintenance interval must be set if item needs maintenance.")

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    class Meta:
        indexes = [
            models.Index(fields=['item_type']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]
        ordering = ['-date_added']


# ------------------------ Item Request ------------------------

class ItemRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('issued', 'Issued'),
        ('return_requested', 'Return Requested'),  # NEW
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests_made")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="requests")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    request_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    issued_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)

    reason = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests_processed")
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests_issued")

    is_deleted = models.BooleanField(default=False)

    def clean(self):
        now = timezone.now()

        if self.status == 'issued':
            if not self.issued_date or not self.issued_by:
                raise ValidationError("Issuer and issued date are required when marking as issued.")
            if self.issued_date > now:
                raise ValidationError("Issued date cannot be in the future.")

        if self.status == 'returned':
            if not self.return_date:
                raise ValidationError("Return date required when marking as returned.")
            if self.return_date > now:
                raise ValidationError("Return date cannot be in the future.")
            if self.issued_date and self.return_date < self.issued_date:
                raise ValidationError("Return date cannot be before issued date.")

        if self.decision_date and self.decision_date > now:
            raise ValidationError("Decision date cannot be in the future.")

    def __str__(self):
        return f"{self.user.username} → {self.item.name} ({self.status})"

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['request_date']),
        ]
        ordering = ['-request_date']


# ------------------------ Maintenance Request ------------------------

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="maintenance_logs")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="maintenance_reports")

    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    reported_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    resolution_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="maintenance_resolved")
    actual_completion_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.status == 'completed' and not self.actual_completion_date:
            raise ValidationError("Actual completion date is required when marking as completed.")

    def __str__(self):
        return f"Maintenance - {self.item.serial_number} → {self.status}"

    class Meta:
        ordering = ['-reported_on']

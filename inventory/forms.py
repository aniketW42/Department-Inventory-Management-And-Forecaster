from django import forms
from .models import InventoryItem, ItemRequest


# ---------- ItemRequest Form ----------

class ItemRequestForm(forms.ModelForm):
    class Meta:
        model = ItemRequest
        fields = ['reason']  # Removed 'quantity' (not applicable for per-item tracking)
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Please specify why you need this item...',
            }),
        }


# ---------- InventoryItem Form ----------

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'serial_number',
            'asset_tag',
            'name',
            'description',
            'item_type',
            'category',
            'location',
            'reorder_level',
            'needs_maintenance',
            'maintenance_interval_days',
            'image',
        ]
        widgets = {
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'needs_maintenance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_interval_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

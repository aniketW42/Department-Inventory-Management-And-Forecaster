from django import forms
from .models import ItemRequest
from .models import InventoryItem

class ItemRequestForm(forms.ModelForm):
    class Meta:
        model = ItemRequest
        fields = ['quantity', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'name',
            'description',
            'item_type',
            'quantity',
            'category',
            'location',
            'reorder_level',
            'needs_maintenance',
            'maintenance_interval_days',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'needs_maintenance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_interval_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

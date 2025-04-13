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

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'name', 'description', 'item_type', 'quantity',
            'category'       ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }
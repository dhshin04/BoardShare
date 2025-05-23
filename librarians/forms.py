from django import forms
from django.contrib.auth.forms import User
from .models import LibrarianItem, Collection, LibrarianItemImage


class LibrarianItemsForm(forms.ModelForm):
    class Meta:
        model = LibrarianItem
        fields = ['title', 'status', 'location', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class LibrarianItemsImageForm(forms.ModelForm):
    class Meta:
        model = LibrarianItemImage
        fields = ['image']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CollectionsForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'is_private']

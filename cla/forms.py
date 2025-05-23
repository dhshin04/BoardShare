from django import forms
from django.contrib.auth.forms import User
from librarians.models import Profile, Collection, Review
from .models import UserType

class LibrarianSignUpForm(forms.ModelForm):
    class Meta:
        model = UserType
        fields = ['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_librarian = True
        if commit:
            user.save()
        return user
    
class PatronSignUpForm(forms.ModelForm):
    class Meta:
        model = UserType
        fields = ['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_librarian = False
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class PatronCollectionsForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description']

class LibrarianCollectionsForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'is_private']

class ReviewsForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={'placeholder': 'Select a rating'}),
        label='Rating'
    )
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)


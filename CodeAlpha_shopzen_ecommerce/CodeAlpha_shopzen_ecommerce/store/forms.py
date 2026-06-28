from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Street Address'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Postal Code'}))
    country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Country'}))

    # Card info (UI only — no real payment processing)
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'}),
        label='Card Number'
    )
    expiry = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}),
        label='Expiry Date'
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'CVV'}),
        label='CVV'
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience...'}),
        }

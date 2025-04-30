from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ShortenedURL

class URLShortenerForm(forms.Form):
    original_url = forms.URLField(
        label="Enter a URL to shorten",
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/very/long/url'})
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
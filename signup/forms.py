from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Event, ClubUser

# forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import PreRegistration


class EAURNLookupForm(forms.Form):
    ea_urn = forms.CharField(
        label="England Athletics URN",
        max_length=64,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Enter your EA URN'
        })
    )

    def clean_ea_urn(self):
        ea_urn = self.cleaned_data['ea_urn']

        # Check if PreRegistration exists with this EA URN
        try:
            PreRegistration.objects.get(ea_urn=ea_urn)
        except PreRegistration.DoesNotExist:
            raise forms.ValidationError("No pre-registration found with this EA URN!!")

        # Check if user already exists with this EA URN
        User = get_user_model()
        if User.objects.filter(ea_urn=ea_urn).exists():
            raise forms.ValidationError("A user account already exists with this EA URN.")

        return ea_urn

class EAEmailLookupForm(forms.Form):
    ea_email = forms.CharField(
        label="Your email address",
        max_length=512,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Enter your email address'
        })
    )

    def clean_ea_email(self):
        ea_email = self.cleaned_data['ea_email']

        # Check if PreRegistration exists with this EA URN
        try:
            PreRegistration.objects.get(email=ea_email)
        except PreRegistration.DoesNotExist:
            raise forms.ValidationError("No pre-registration found with this email address")

        # Check if user already exists
        User = get_user_model()
        if User.objects.filter(email=ea_email).exists():
            raise forms.ValidationError("A user account already exists with this mail address.")

        return ea_email



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = ClubUser
        fields = ("username", "first_name", "last_name", "birth_date", "email", "password1", "password2")

    def __init__(self, preregistration=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500'

        # Make birth_date required and add date widget
        self.fields['birth_date'].required = True
        self.fields['birth_date'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500'
            }
        )

        # Pre-fill fields if preregistration data is provided
        if preregistration:
            self.fields['first_name'].initial = preregistration.first_name
            self.fields['last_name'].initial = preregistration.last_name
            self.fields['email'].initial = preregistration.email
            self.fields['birth_date'].initial = preregistration.birth_date

            # Optionally suggest a username based on their name
            suggested_username = f"{preregistration.first_name.lower()}.{preregistration.last_name.lower()}"
            self.fields['username'].initial = suggested_username
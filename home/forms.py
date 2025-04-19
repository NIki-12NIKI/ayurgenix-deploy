from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile  # Only import UserProfile
from datetime import date
import re
from django.core.exceptions import ValidationError
from PIL import Image

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required")
        return email.lower().strip()

class UserProfileForm(forms.ModelForm):
    # Include fields from User model that we want to edit
    email = forms.EmailField(required=True)
    username = forms.CharField(disabled=True, required=False)  # Read-only

    def clean_birth_year(self):
        birth_year = self.cleaned_data.get('birth_year')
        if birth_year:
            today = date.today()
            age = today.year - birth_year
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        return birth_year

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and not (50 <= height <= 300):
            raise forms.ValidationError("Please enter a valid height in centimeters (50-300).")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and not (20 <= weight <= 500):
            raise forms.ValidationError("Please enter a valid weight in kilograms (20-500).")
        return weight

    class Meta:
        model = UserProfile
        exclude = ['user', 'bmi', 'profile_completion_percentage', 'last_updated']
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'dosha_type': 'Predominant Dosha',
            'bmi': 'BMI (Auto-calculated)',
            'height': 'Height (in cm)',
            'weight': 'Weight (in kg)',
        }
        help_texts = {
            'medical_history': 'List any past surgeries, conditions, or treatments.',
            'allergies': 'List any known allergies.',
            'dosha_type': 'Select your primary dosha type based on assessment.',
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower().strip()
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        if commit:
            user.save()
        return user

class ProfileEditForm(forms.ModelForm):
    # Include fields from User model that we want to edit
    email = forms.EmailField(required=True)
    username = forms.CharField(disabled=True, required=False)  # Read-only

    # Explicitly define choices for blood_group and dosha_type
    blood_group = forms.ChoiceField(choices=UserProfile.BLOOD_GROUP_CHOICES, required=False)
    dosha_type = forms.ChoiceField(choices=UserProfile.DOSHA_CHOICES, required=False)

    class Meta:
        model = UserProfile
        exclude = ['user', 'bmi', 'profile_completion_percentage', 'last_updated']
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
        }
from django.db import models
from django.contrib.auth.models import User
from datetime import date

class UserProfile(models.Model):
    """Model to store user health profile and Ayurvedic details."""

    # Gender Choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ]

    # Blood Group Choices (Fixed missing 'AB-' and incorrect 'B-')
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ('Unknown', 'Unknown'),
    ]

    # Dosha Type Choices
    DOSHA_CHOICES = [
        ('Vata', 'Vata'), ('Pitta', 'Pitta'), ('Kapha', 'Kapha'),
        ('Vata-Pitta', 'Vata-Pitta'), ('Pitta-Kapha', 'Pitta-Kapha'),
        ('Vata-Kapha', 'Vata-Kapha'), ('Tridoshic', 'Tridoshic'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True, default='')
    last_name = models.CharField(max_length=50, blank=True, default='')
    birth_year = models.IntegerField(null=True, blank=True, help_text="Year of birth (e.g., 1998)")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, default='')
    height = models.FloatField(null=True, blank=True, help_text='Height in cm')
    weight = models.FloatField(null=True, blank=True, help_text='Weight in kg')
    blood_group = models.CharField(max_length=7, choices=BLOOD_GROUP_CHOICES, default='Unknown')
    medical_history = models.TextField(blank=True, default='', help_text='Comma-separated past diseases or conditions')
    dosha_type = models.CharField(max_length=50, choices=DOSHA_CHOICES, blank=True, default='', help_text='Select your Ayurvedic body type')
    allergies = models.TextField(blank=True, default='', help_text='Known allergies')
    bmi = models.FloatField(null=True, blank=True)
    profile_completion_percentage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_bmi(self):
        """Calculates BMI based on height and weight."""
        if self.height and self.weight:
            return round(self.weight / ((self.height / 100) ** 2), 2)
        return None

    def calculate_age(self):
        """Calculates age dynamically based on birth year."""
        if self.birth_year and self.birth_year <= date.today().year:
            return date.today().year - self.birth_year
        return None  # Prevents negative ages

    def calculate_profile_completion(self):
        """Calculates profile completion percentage dynamically."""
        all_fields = [
            self.first_name, self.last_name, self.birth_year, self.gender, 
            self.height, self.weight, self.blood_group, self.medical_history,
            self.dosha_type, self.allergies  # Included missing fields
        ]
        filled_fields = sum(1 for field in all_fields if field)
        return int((filled_fields / len(all_fields)) * 100)

    def save(self, *args, **kwargs):
        """Auto-calculates BMI and profile completion before saving."""
        self.bmi = self.calculate_bmi()
        self.profile_completion_percentage = self.calculate_profile_completion()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.calculate_age()} years old)"


class ChatConversation(models.Model):
    """Stores chatbot interactions with AI-generated responses."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    symptoms = models.TextField(blank=True, default='')
    user_message = models.TextField(blank=True, default='')  
    ai_response = models.TextField(blank=True, default='')  
    predictions = models.JSONField(blank=True, default=dict, help_text="Stores AI-generated predictions")
    treatment = models.JSONField(blank=True, default=dict, help_text="Stores AI-recommended treatments")
    confidence_score = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

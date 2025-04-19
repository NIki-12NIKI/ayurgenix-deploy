from django.urls import path
from .views import landing_page  # Import your view



urlpatterns = [
    path('', landing_page, name='landing_page'),
]


from django.urls import path
from .views import landing_page, generate_response_view

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('api/ayurgenix/', generate_response_view, name='ayurgenix-api'),
]

from django.urls import path
from home import views

urlpatterns = [
    # Main pages
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact_page'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # First-time login redirection
    path('after-login/', views.after_login_redirect, name='after_login'),
    
    # Profile Management
    path('make-profile/', views.make_profile, name='make_profile'),
    path('profile/view/<int:user_id>/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Chatbot
    path('chat/', views.chat_page, name='chat_page'),
    path('api/chat/', views.chat_api, name='chat_api'),  # ✅ Added correct mapping for chat_api
    path('api/chat/send-message/', views.send_message, name='send_message'),
    path('api/chat/get-chat-history/', views.get_chat_history, name='get_chat_history'),
    
]

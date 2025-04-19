from django.contrib import admin
from .models import UserProfile, ChatConversation  # Import the correct models

# Register the UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'gender', 'blood_group', 'dosha_type', 'profile_completion_percentage')
    search_fields = ('user__username', 'first_name', 'last_name', 'dosha_type')
    list_filter = ('gender', 'blood_group', 'dosha_type')

# Register the ChatConversation model
@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'user_message', 'ai_response', 'confidence_score')
    search_fields = ('user__username', 'user_message', 'ai_response')
    list_filter = ('timestamp', 'confidence_score')
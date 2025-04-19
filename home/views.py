import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

# Import models consistently from the local app
from .models import UserProfile, ChatConversation
from .forms import UserProfileForm, ProfileEditForm
from .llm_utils import  generate_ayurvedic_response

# Landing Page
def landing_page(request):
    return render(request, 'home/landing_page.html')

# About Page
def about(request):
    return render(request, 'home/about.html')

# Contact Page
def contact_view(request):
    return render(request, 'home/contact.html')

# Authentication Views
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('after_login')  # Redirect to after_login_redirect view
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'auth/login.html')

@login_required
def after_login_redirect(request):
    """Redirect users based on profile completion."""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not user_profile.calculate_profile_completion():
        return redirect('make_profile')  # Redirect new users to complete profile

    return redirect('dashboard')  # Redirect to dashboard if profile is complete

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not password1 or not password2:
            messages.error(request, "Both password fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        UserProfile.objects.create(user=user)

        login(request, user)

        messages.success(request, "Registration successful. Please complete your profile.")
        return redirect('make_profile')  # Redirect new user to profile completion page

    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('landing_page')

# Profile Management
@login_required
def make_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # If profile is already complete, redirect to the dashboard
    if user_profile.calculate_profile_completion():
        messages.info(request, "Your profile is already complete.")
        return redirect('dashboard')  # Redirect to dashboard

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Ensure any custom fields are correctly set
            if 'email' in form.cleaned_data:
                request.user.email = form.cleaned_data['email']
                request.user.save()
                
            profile.save()

            if profile.calculate_profile_completion():
                messages.success(request, "Profile completed successfully!")
                return redirect('dashboard')  # Redirect to dashboard after completion
            else:
                messages.warning(request, "Profile updated, but some fields are still missing.")
                return redirect('make_profile')
        else:
            # Form is invalid, show error message
            messages.error(request, "There were errors in your profile form. Please fix them and try again.")
    else:
        # Initialize form with email from User model
        initial_data = {'email': request.user.email, 'username': request.user.username}
        form = UserProfileForm(instance=user_profile, initial=initial_data)

    return render(request, 'profile/make_profile.html', {'form': form})

@login_required
def edit_profile(request):
    """Allow users to edit their profile after creation."""
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Handle email update
            if 'email' in form.cleaned_data:
                user.email = form.cleaned_data['email']
                user.save()
                
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "There were errors in your form. Please correct them and try again.")
    else:
        # Initialize form with email from User model
        initial_data = {'email': user.email, 'username': user.username}
        form = ProfileEditForm(instance=user_profile, initial=initial_data)
    
    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def view_profile(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    return render(request, 'profile/view_profile.html', {'profile': profile})

@login_required
def chat_page(request):
    return render(request, "home/chat_page.html")

@login_required
def chat_view(request):
    """Render the chat page."""
    # Get previous messages if you want to display chat history
    previous_messages = ChatConversation.objects.filter(user=request.user).order_by('timestamp')[:20]
    return render(request, 'chat_page.html', {'previous_messages': previous_messages})

from .llm_utils import generate_ayurvedic_response

@login_required
@csrf_exempt
def chat_api(request):
    """Handles chatbot interaction with optimized model loading."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            # Generate AI response using fine-tuned LLaMA model
            ai_response = generate_ayurvedic_response(user_message)

            # Save conversation to the database (only once)
            chat_entry = ChatConversation.objects.create(
                user=request.user,
                user_message=user_message,
                ai_response=ai_response,
                confidence_score=0.9  # Example confidence score
            )

            return JsonResponse({
                "status": "success",
                "user_message": chat_entry.user_message,
                "ai_response": chat_entry.ai_response
            })

        except Exception as e:
            print(f"❌ Chatbot Error: {e}")
            return JsonResponse({"error": "AI model encountered an issue. Please try again."}, status=500)

    return JsonResponse({"error": "Invalid request. Only POST allowed."}, status=400)


@csrf_exempt
@login_required
def send_message(request):
    """Handle sending messages to the Gemini API and receiving responses."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Save user message to database
            ChatConversation.objects.create(
                user=request.user,
                user_message=user_message,
                ai_response="",  # AI response will be updated later
                predictions={},
                treatment={},
                confidence_score=0.0
            )

            # Get user profile for personalized responses
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = None

            # Generate AI response using Gemini
            ai_response = generate_ayurvedic_response(user_message, user_profile)

            # Save AI response to database
            ChatConversation.objects.create(
                user=request.user,
                user_message="",  # Empty user message for AI response
                ai_response=ai_response,
                predictions={},
                treatment={},
                confidence_score=0.9  # Example confidence score
            )

            return JsonResponse({'response': ai_response})

        except Exception as e:
            print(f"Error processing message: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def get_chat_history(request):
    chat_messages = ChatConversation.objects.filter(user=request.user).values()
    return JsonResponse({"chat_history": list(chat_messages)})

# Dashboard View
@login_required
@login_required
def dashboard(request):
    # Get the logged-in user's profile
    user = request.user
    
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create a profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=user)
        messages.info(request, "We've created a profile for you. Please complete it.")
        return redirect('make_profile')
    
    # Fetch chat history for the logged-in user
    chat_history = ChatConversation.objects.filter(user=user).order_by('-timestamp')[:10]
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'chat_history': chat_history,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
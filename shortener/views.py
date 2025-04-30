
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.db.models import Count
from .models import ShortenedURL, ClickAnalytics
from .forms import URLShortenerForm, CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth import get_user_model

# Create your views here.

def home(request):
    """Home page with URL shortening form for all users"""
    form = URLShortenerForm()
    shortened_url = None

    if request.method == 'POST':
        form = URLShortenerForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['original_url']
            owner = request.user if request.user.is_authenticated else None
            shortened_url = ShortenedURL.create_short_url(original_url, owner)
            
            # Reset form for new submission
            form = URLShortenerForm()
            
    return render(request, 'home.html', {
        'form': form,
        'shortened_url': shortened_url,
        'domain': request.get_host(),
    })

def redirect_to_original(request, short_alias):
    """Handle redirection from short URL to original URL"""
    try:
        url_obj = ShortenedURL.objects.get(short_alias=short_alias)
        
        # Record the click
        ClickAnalytics.objects.create(
            shortened_url=url_obj,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )
        
        return HttpResponseRedirect(url_obj.original_url)
    except ShortenedURL.DoesNotExist:
        raise Http404("Short URL does not exist")


class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    def form_invalid(self, form):
        """Add a message when login fails"""
        username = form.data.get('username')
        # Check if the username exists
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            messages.error(
                self.request, 
                f"Account with username '{username}' doesn't exist. Please register first."
            )
        else:
            messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')

@login_required
def dashboard(request):
    """User dashboard showing all their shortened URLs"""
    user_urls = ShortenedURL.objects.filter(owner=request.user).annotate(
        click_count=Count('clicks')
    ).order_by('-creation_date')
    
    return render(request, 'dashboard.html', {
        'user_urls': user_urls,
        'domain': request.get_host(),
    })

@login_required
def link_detail(request, short_alias):
    """Detailed view of a specific shortened URL"""
    url_obj = get_object_or_404(ShortenedURL, short_alias=short_alias, owner=request.user)
    clicks = ClickAnalytics.objects.filter(shortened_url=url_obj).order_by('-click_timestamp')
    
    return render(request, 'link_detail.html', {
        'url_obj': url_obj,
        'clicks': clicks,
        'domain': request.get_host(),
        'click_count': clicks.count(),
    })

@login_required
def delete_link(request, short_alias):
    """Delete a shortened URL"""
    url_obj = get_object_or_404(ShortenedURL, short_alias=short_alias, owner=request.user)
    
    if request.method == 'POST':
        url_obj.delete()
        messages.success(request, "URL has been deleted successfully.")
        return redirect('dashboard')
    
    return render(request, 'confirm_delete.html', {'url_obj': url_obj})

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f"Account created for {username}. You are now logged in.")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

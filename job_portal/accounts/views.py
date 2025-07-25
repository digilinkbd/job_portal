from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegistrationForm, JobSeekerProfileForm, EmployerProfileForm, LoginForm
from .models import User, JobSeekerProfile, EmployerProfile

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect based on user type
                if user.user_type == 'employer':
                    return redirect('jobs:employer_dashboard')
                else:
                    return redirect('jobs:job_list')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'job_seeker':
        profile = get_object_or_404(JobSeekerProfile, user=user)
        context['profile'] = profile
        template = 'accounts/job_seeker_profile.html'
    else:
        profile = get_object_or_404(EmployerProfile, user=user)
        context['profile'] = profile
        template = 'accounts/employer_profile.html'
    
    return render(request, template, context)

@login_required
def edit_profile_view(request):
    user = request.user
    
    if user.user_type == 'job_seeker':
        profile = get_object_or_404(JobSeekerProfile, user=user)
        form_class = JobSeekerProfileForm
        template = 'accounts/edit_job_seeker_profile.html'
    else:
        profile = get_object_or_404(EmployerProfile, user=user)
        form_class = EmployerProfileForm
        template = 'accounts/edit_employer_profile.html'
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = form_class(instance=profile)
    
    return render(request, template, {'form': form, 'profile': profile})

def dashboard_redirect(request):
    """Redirect users to appropriate dashboard based on their role"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.user_type == 'employer':
        return redirect('jobs:employer_dashboard')
    else:
        return redirect('jobs:job_list')
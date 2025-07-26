# accounts/views.py - Authentication and Profile Views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import User, JobSeekerProfile, EmployerProfile
from .forms import (
    JobSeekerRegistrationForm, EmployerRegistrationForm, CustomLoginForm,
    JobSeekerProfileForm, EmployerProfileForm, UserUpdateForm
)

# Authentication Views
class CustomLoginView(LoginView):
    """Custom login view with email support"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect based on user type"""
        if self.request.user.user_type == 'job_seeker':
            return reverse_lazy('accounts:job_seeker_dashboard')
        elif self.request.user.user_type == 'employer':
            return reverse_lazy('jobs:employer_dashboard')
        return reverse_lazy('jobs:job_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

def register_choice(request):
    """Registration choice page"""
    return render(request, 'accounts/register_choice.html')

def job_seeker_register(request):
    """Job seeker registration"""
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the job portal.')
            return redirect('accounts:job_seeker_profile_setup')
    else:
        form = JobSeekerRegistrationForm()
    
    return render(request, 'accounts/job_seeker_register.html', {'form': form})

def employer_register(request):
    """Employer registration"""
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the employer portal.')
            return redirect('accounts:employer_profile_setup')
    else:
        form = EmployerRegistrationForm()
    
    return render(request, 'accounts/employer_register.html', {'form': form})

@login_required
def custom_logout(request):
    """Custom logout with message"""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('jobs:job_list')

# Dashboard Views
@login_required
def job_seeker_dashboard(request):
    """Job seeker dashboard"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_list')
    
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    # Get user statistics
    from jobs.models import JobApplication, SavedJob
    stats = {
        'applications_count': JobApplication.objects.filter(applicant=profile).count(),
        'saved_jobs_count': SavedJob.objects.filter(user=profile).count(),
        'profile_completeness': profile.calculate_profile_completeness(),
    }
    
    # Get recent applications
    recent_applications = JobApplication.objects.filter(
        applicant=profile
    ).select_related('job', 'job__company').order_by('-applied_date')[:5]
    
    # Get recommended jobs (based on skills and preferences)
    from jobs.models import Job
    recommended_jobs = Job.objects.filter(status='active')
    if profile.skills:
        skills_list = profile.get_skills_list()
        skill_query = Q()
        for skill in skills_list:
            skill_query |= Q(required_skills__icontains=skill)
        recommended_jobs = recommended_jobs.filter(skill_query)
    
    recommended_jobs = recommended_jobs[:5]
    
    context = {
        'profile': profile,
        'stats': stats,
        'recent_applications': recent_applications,
        'recommended_jobs': recommended_jobs,
    }
    
    return render(request, 'accounts/job_seeker_dashboard.html', context)

@login_required
def employer_dashboard(request):
    """Employer dashboard with job and application statistics"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_list')
    
    profile = get_object_or_404(EmployerProfile, user=request.user)
    
    # This view is already implemented in jobs/views.py
    # Redirect to the existing employer dashboard
    return redirect('jobs:employer_dashboard')

# Profile Management Views
@login_required
def job_seeker_profile_setup(request):
    """Initial profile setup for job seekers"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_list')
    
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile setup completed successfully!')
            return redirect('accounts:job_seeker_dashboard')
    else:
        profile_form = JobSeekerProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'is_setup': True,
    }
    
    return render(request, 'accounts/job_seeker_profile_form.html', context)

@login_required
def employer_profile_setup(request):
    """Initial profile setup for employers"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_list')
    
    profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Company profile setup completed successfully!')
            return redirect('jobs:employer_dashboard')
    else:
        profile_form = EmployerProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'is_setup': True,
    }
    
    return render(request, 'accounts/employer_profile_form.html', context)

@login_required
def job_seeker_profile(request):
    """Job seeker profile view and edit"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_list')
    
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:job_seeker_profile')
    else:
        profile_form = JobSeekerProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)
    
    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'completeness': profile.calculate_profile_completeness(),
    }
    
    return render(request, 'accounts/job_seeker_profile.html', context)

@login_required
def employer_profile(request):
    """Employer profile view and edit"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_list')
    
    profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Company profile updated successfully!')
            return redirect('accounts:employer_profile')
    else:
        profile_form = EmployerProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)
    
    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'completeness': profile.calculate_profile_completeness(),
    }
    
    return render(request, 'accounts/employer_profile.html', context)

# Public Profile Views
def job_seeker_public_profile(request, pk):
    """Public view of job seeker profile (for employers)"""
    profile = get_object_or_404(JobSeekerProfile, pk=pk)
    
    # Check privacy settings
    if profile.profile_visibility == 'private':
        if not request.user.is_authenticated or request.user != profile.user:
            messages.error(request, 'This profile is private.')
            return redirect('jobs:job_list')
    elif profile.profile_visibility == 'employers_only':
        if not request.user.is_authenticated or request.user.user_type != 'employer':
            messages.error(request, 'This profile is only visible to employers.')
            return redirect('jobs:job_list')
    
    # Get job seeker's application history (if viewing own profile or employer)
    applications = None
    if (request.user.is_authenticated and 
        (request.user == profile.user or request.user.user_type == 'employer')):
        from jobs.models import JobApplication
        applications = JobApplication.objects.filter(
            applicant=profile
        ).select_related('job').order_by('-applied_date')[:10]
    
    context = {
        'profile': profile,
        'applications': applications,
        'is_own_profile': request.user.is_authenticated and request.user == profile.user,
    }
    
    return render(request, 'accounts/job_seeker_public_profile.html', context)

def employer_public_profile(request, pk):
    """Public view of employer profile"""
    profile = get_object_or_404(EmployerProfile, pk=pk)
    
    # Get company's active jobs
    from jobs.models import Job
    active_jobs = Job.objects.filter(
        company=profile, status='active'
    ).order_by('-created_at')[:10]
    
    context = {
        'profile': profile,
        'active_jobs': active_jobs,
        'is_own_profile': request.user.is_authenticated and request.user == profile.user,
    }
    
    return render(request, 'accounts/employer_public_profile.html', context)

# Settings and Preferences
@login_required
def account_settings(request):
    """Account settings and preferences"""
    context = {
        'user': request.user,
    }
    
    if request.user.user_type == 'job_seeker':
        context['profile'] = get_object_or_404(JobSeekerProfile, user=request.user)
    elif request.user.user_type == 'employer':
        context['profile'] = get_object_or_404(EmployerProfile, user=request.user)
    
    return render(request, 'accounts/account_settings.html', context)

@login_required
@require_http_methods(["POST"])
def delete_account(request):
    """Delete user account"""
    if request.POST.get('confirm_delete') == 'DELETE':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('jobs:job_list')
    else:
        messages.error(request, 'Account deletion confirmation failed.')
        return redirect('accounts:account_settings')

# AJAX Views
@login_required
def check_profile_completeness(request):
    """AJAX endpoint to check profile completeness"""
    if request.user.user_type == 'job_seeker':
        profile = get_object_or_404(JobSeekerProfile, user=request.user)
    elif request.user.user_type == 'employer':
        profile = get_object_or_404(EmployerProfile, user=request.user)
    else:
        return JsonResponse({'error': 'Invalid user type'}, status=400)
    
    completeness = profile.calculate_profile_completeness()
    
    return JsonResponse({
        'completeness': completeness,
        'is_complete': profile.is_profile_complete,
    })
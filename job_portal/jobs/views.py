from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Job, JobCategory, JobApplication, SavedJob
from .forms import JobForm, JobSearchForm, JobApplicationForm, ApplicationStatusForm
from accounts.models import EmployerProfile, JobSeekerProfile

# Public Views
def job_list(request):
    """Display all active jobs with search and filter functionality"""
    jobs = Job.objects.filter(status='active').select_related('company', 'category')
    form = JobSearchForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')
        experience_level = form.cleaned_data.get('experience_level')
        location = form.cleaned_data.get('location')
        is_remote = form.cleaned_data.get('is_remote')
        salary_min = form.cleaned_data.get('salary_min')
        sort_by = form.cleaned_data.get('sort_by') or '-created_at'
        
        # Apply filters
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(company__company_name__icontains=search) |
                Q(description__icontains=search) |
                Q(required_skills__icontains=search)
            )
        
        if category:
            jobs = jobs.filter(category=category)
        
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
        
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        if is_remote:
            jobs = jobs.filter(is_remote=True)
        
        if salary_min:
            jobs = jobs.filter(salary_min__gte=salary_min)
        
        # Apply sorting (ensure sort_by is not empty)
        if sort_by:
            jobs = jobs.order_by(sort_by)
        else:
            jobs = jobs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_jobs': jobs.count(),
    }
    
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    """Display detailed view of a job"""
    job = get_object_or_404(Job, pk=pk, status='active')
    
    # Increment view count
    job.increment_views()
    
    # Check if user has applied (for job seekers)
    has_applied = False
    is_saved = False
    
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        job_seeker_profile = getattr(request.user, 'job_seeker_profile', None)
        if job_seeker_profile:
            has_applied = JobApplication.objects.filter(
                job=job, applicant=job_seeker_profile
            ).exists()
            is_saved = SavedJob.objects.filter(
                job=job, user=job_seeker_profile
            ).exists()
    
    # Get related jobs (same category)
    related_jobs = Job.objects.filter(
        category=job.category, status='active'
    ).exclude(pk=job.pk)[:3]
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_saved': is_saved,
        'related_jobs': related_jobs,
    }
    
    return render(request, 'jobs/job_detail.html', context)

# Employer Views
@login_required
def employer_dashboard(request):
    """Employer dashboard showing job statistics and recent applications"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    
    # Get job statistics
    jobs = Job.objects.filter(company=employer_profile)
    job_stats = {
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'draft_jobs': jobs.filter(status='draft').count(),
        'closed_jobs': jobs.filter(status='closed').count(),
    }
    
    # Get recent applications
    recent_applications = JobApplication.objects.filter(
        job__company=employer_profile
    ).select_related('job', 'applicant__user').order_by('-applied_date')[:5]
    
    # Get application statistics
    app_stats = JobApplication.objects.filter(job__company=employer_profile).aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        reviewed=Count('id', filter=Q(status='reviewed')),
        shortlisted=Count('id', filter=Q(status='shortlisted'))
    )
    
    context = {
        'job_stats': job_stats,
        'recent_applications': recent_applications,
        'app_stats': app_stats,
    }
    
    return render(request, 'jobs/employer_dashboard.html', context)

@login_required
def employer_jobs(request):
    """List all jobs posted by the employer"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    jobs = Job.objects.filter(company=employer_profile).order_by('-created_at')
    
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'jobs/employer_jobs.html', context)

@login_required
def create_job(request):
    """Create a new job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = employer_profile
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm()
    
    return render(request, 'jobs/create_job.html', {'form': form})

@login_required
def edit_job(request, pk):
    """Edit an existing job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    job = get_object_or_404(Job, pk=pk, company=employer_profile)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs:job_detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, pk):
    """Delete a job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    job = get_object_or_404(Job, pk=pk, company=employer_profile)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('jobs:employer_jobs')
    
    return render(request, 'jobs/delete_job.html', {'job': job})

# Job Seeker Views
@login_required
def apply_job(request, pk):
    """Apply for a job"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied. Job seekers only.')
        return redirect('jobs:job_detail', pk=pk)
    
    job = get_object_or_404(Job, pk=pk, status='active')
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=job_seeker_profile).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = job_seeker_profile
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('jobs:job_detail', pk=pk)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

@login_required
@require_POST
def save_job(request, pk):
    """Save/unsave a job"""
    if request.user.user_type != 'job_seeker':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    job = get_object_or_404(Job, pk=pk)
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    saved_job, created = SavedJob.objects.get_or_create(
        job=job, user=job_seeker_profile
    )
    
    if not created:
        saved_job.delete()
        return JsonResponse({'saved': False, 'message': 'Job removed from saved jobs'})
    
    return JsonResponse({'saved': True, 'message': 'Job saved successfully'})

@login_required
def my_applications(request):
    """List user's job applications"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied. Job seekers only.')
        return redirect('jobs:job_list')
    
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    applications = JobApplication.objects.filter(
        applicant=job_seeker_profile
    ).select_related('job', 'job__company').order_by('-applied_date')
    
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/my_applications.html', {'page_obj': page_obj})

@login_required
def saved_jobs(request):
    """List user's saved jobs"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied. Job seekers only.')
        return redirect('jobs:job_list')
    
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    saved_jobs = SavedJob.objects.filter(
        user=job_seeker_profile
    ).select_related('job', 'job__company').order_by('-saved_date')
    
    paginator = Paginator(saved_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/saved_jobs.html', {'page_obj': page_obj})
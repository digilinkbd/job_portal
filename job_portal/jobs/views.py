from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth import get_user_model
from urllib.parse import urlencode

from .models import Job, JobCategory, JobApplication, SavedJob
from .forms import JobForm, JobSearchForm, JobApplicationForm, ApplicationStatusForm
from accounts.models import EmployerProfile, JobSeekerProfile

# ADD THIS NEW VIEW AT THE BEGINNING (before your existing views)
def home(request):
    """Homepage with job search, featured jobs, and statistics"""
    
    # Get featured/recent jobs (latest 6 active jobs)
    featured_jobs = Job.objects.filter(status='active').select_related(
        'company', 'category'
    ).order_by('-created_at')[:6]
    
    # Get job statistics
    total_jobs = Job.objects.filter(status='active').count()
    total_companies = EmployerProfile.objects.count()
    
    # Count job seekers (users with job_seeker user_type)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    total_job_seekers = User.objects.filter(user_type='job_seeker').count()
    
    # Get popular job categories with job counts
    popular_categories = JobCategory.objects.annotate(
        job_count=Count('job', filter=Q(job__status='active'))
    ).filter(job_count__gt=0).order_by('-job_count')[:8]
    
    # Get recent job locations
    recent_locations = Job.objects.filter(
        status='active'
    ).values_list('location', flat=True).distinct()[:10]
    
    # Process search if coming from homepage search
    if request.GET.get('q') or request.GET.get('location'):
        search_query = request.GET.get('q', '')
        location_query = request.GET.get('location', '')
        
        # Redirect to job list page with search parameters
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from urllib.parse import urlencode
        
        params = {}
        if search_query:
            params['search'] = search_query
        if location_query:
            params['location'] = location_query
            
        if params:
            return HttpResponseRedirect(reverse('jobs:job_list') + '?' + urlencode(params))
    
    context = {
        'featured_jobs': featured_jobs,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_job_seekers': total_job_seekers,
        'popular_categories': popular_categories,
        'recent_locations': recent_locations,
    }
    
    return render(request, 'jobs/home.html', context)

# Public Views
def job_list(request):
    """Display list of all active jobs with search and filtering"""
    jobs = Job.objects.filter(status='active').select_related('company', 'category').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__company_name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        jobs = jobs.filter(category_id=category_id)
    
    # Location filter
    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Job type filter
    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Salary range filter
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)
    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # Show 12 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = JobCategory.objects.all()
    
    # Get unique locations for filter
    locations = Job.objects.filter(status='active').values_list('location', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'categories': categories,
        'locations': locations,
        'selected_category': category_id,
        'selected_location': location,
        'selected_job_type': job_type,
        'salary_min': salary_min,
        'salary_max': salary_max,
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
def quick_apply(request, pk):
    """Quick apply for a job (AJAX endpoint)"""
    if request.user.user_type != 'job_seeker':
        return JsonResponse({'error': 'Access denied. Job seekers only.'}, status=403)
    
    job = get_object_or_404(Job, pk=pk, status='active')
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=job_seeker_profile).exists():
        return JsonResponse({
            'success': False, 
            'message': 'You have already applied for this job.'
        }, status=400)
    
    # Create quick application (without cover letter/resume upload)
    application = JobApplication.objects.create(
        job=job,
        applicant=job_seeker_profile,
        cover_letter='Quick application submitted',
        resume=job_seeker_profile.resume if hasattr(job_seeker_profile, 'resume') else None
    )
    
    return JsonResponse({
        'success': True, 
        'message': 'Application submitted successfully!'
    })

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
def application_detail(request, pk):
    """View application details for job seeker"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied. Job seekers only.')
        return redirect('jobs:job_list')
    
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    application = get_object_or_404(
        JobApplication, 
        pk=pk, 
        applicant=job_seeker_profile
    )
    
    return render(request, 'jobs/application_detail.html', {'application': application})

@login_required
@require_POST
def withdraw_application(request, pk):
    """Withdraw a job application"""
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied. Job seekers only.')
        return redirect('jobs:job_list')
    
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)
    application = get_object_or_404(
        JobApplication, 
        pk=pk, 
        applicant=job_seeker_profile
    )
    
    # Only allow withdrawal if application is still pending
    if application.status != 'pending':
        messages.error(request, 'Cannot withdraw application that has already been processed.')
        return redirect('jobs:my_applications')
    
    application.delete()
    messages.success(request, 'Application withdrawn successfully.')
    return redirect('jobs:my_applications')

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

# Employer Application Management Views
@login_required
def job_applications(request, job_pk):
    """View applications for a specific job (Employer view)"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    job = get_object_or_404(Job, pk=job_pk, company=employer_profile)
    
    applications = JobApplication.objects.filter(job=job).select_related(
        'applicant__user'
    ).order_by('-applied_date')
    
    # Filter by status if specified
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get application statistics
    app_stats = JobApplication.objects.filter(job=job).aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        reviewed=Count('id', filter=Q(status='reviewed')),
        shortlisted=Count('id', filter=Q(status='shortlisted')),
        rejected=Count('id', filter=Q(status='rejected'))
    )
    
    context = {
        'job': job,
        'page_obj': page_obj,
        'app_stats': app_stats,
        'status_filter': status_filter,
    }
    
    return render(request, 'jobs/job_applications.html', context)

@login_required
def application_detail_employer(request, pk):
    """View application details for employer"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employers only.')
        return redirect('jobs:job_list')
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    application = get_object_or_404(
        JobApplication, 
        pk=pk, 
        job__company=employer_profile
    )
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application status updated successfully.')
            return redirect('jobs:application_detail_employer', pk=pk)
    else:
        form = ApplicationStatusForm(instance=application)
    
    context = {
        'application': application,
        'form': form,
    }
    
    return render(request, 'jobs/application_detail_employer.html', context)

@login_required
@require_POST
def bulk_update_applications(request):
    """Bulk update application statuses"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    
    application_ids = request.POST.getlist('application_ids')
    new_status = request.POST.get('status')
    
    if not application_ids or not new_status:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    # Update applications
    updated_count = JobApplication.objects.filter(
        id__in=application_ids,
        job__company=employer_profile
    ).update(status=new_status)
    
    return JsonResponse({
        'success': True,
        'message': f'{updated_count} applications updated successfully.'
    })

# Utility Views
def job_categories(request):
    """List all job categories"""
    categories = JobCategory.objects.annotate(
        job_count=Count('job', filter=Q(job__status='active'))
    ).order_by('name')
    
    return render(request, 'jobs/job_categories.html', {'categories': categories})

def jobs_by_category(request, pk):
    """List jobs by category"""
    category = get_object_or_404(JobCategory, pk=pk)
    jobs = Job.objects.filter(
        category=category, 
        status='active'
    ).select_related('company').order_by('-created_at')
    
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'jobs/jobs_by_category.html', context)

def jobs_by_company(request, pk):
    """List jobs by company"""
    company = get_object_or_404(EmployerProfile, pk=pk)
    jobs = Job.objects.filter(
        company=company, 
        status='active'
    ).order_by('-created_at')
    
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'company': company,
        'page_obj': page_obj,
    }
    
    return render(request, 'jobs/jobs_by_company.html', context)
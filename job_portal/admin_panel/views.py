from django.shortcuts import render

# Create your views here.
# admin_panel/views.py - Custom Admin Panel Views

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json
import csv

from accounts.models import User, JobSeekerProfile, EmployerProfile
from jobs.models import Job, JobApplication, SavedJob, JobCategory
from django.contrib.auth import get_user_model

User = get_user_model()

# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.user_type == 'admin')

def is_staff_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.user_type == 'admin')

# Main Admin Dashboard
@login_required
@user_passes_test(is_staff_or_admin)
def admin_dashboard(request):
    """Main admin dashboard with comprehensive statistics"""
    
    # Time range filter
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # User Statistics
    total_users = User.objects.count()
    job_seekers = User.objects.filter(user_type='job_seeker').count()
    employers = User.objects.filter(user_type='employer').count()
    new_users_this_period = User.objects.filter(date_joined__gte=start_date).count()
    
    # Job Statistics
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status='active').count()
    jobs_this_period = Job.objects.filter(created_at__gte=start_date).count()
    
    # Application Statistics
    total_applications = JobApplication.objects.count()
    applications_this_period = JobApplication.objects.filter(applied_date__gte=start_date).count()
    
    # Application Status Distribution
    application_status_data = JobApplication.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Top Categories
    top_categories = JobCategory.objects.annotate(
        job_count=Count('job', filter=Q(job__status='active'))
    ).order_by('-job_count')[:5]
    
    # Recent Activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_applications = JobApplication.objects.select_related(
        'job', 'applicant', 'applicant__user'
    ).order_by('-applied_date')[:10]
    
    # Chart Data for Analytics
    # Daily registrations for the last 30 days
    daily_registrations = []
    for i in range(30):
        day = timezone.now() - timedelta(days=i)
        count = User.objects.filter(
            date_joined__date=day.date()
        ).count()
        daily_registrations.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    daily_registrations.reverse()
    
    # Monthly job postings
    monthly_jobs = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        count = Job.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_jobs.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    monthly_jobs.reverse()
    
    context = {
        'total_users': total_users,
        'job_seekers': job_seekers,
        'employers': employers,
        'new_users_this_period': new_users_this_period,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'jobs_this_period': jobs_this_period,
        'total_applications': total_applications,
        'applications_this_period': applications_this_period,
        'application_status_data': list(application_status_data),
        'top_categories': top_categories,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'daily_registrations': daily_registrations,
        'monthly_jobs': monthly_jobs,
        'days': days,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

# User Management
@login_required
@user_passes_test(is_admin)
def user_management(request):
    """User management interface"""
    
    # Filters
    user_type = request.GET.get('user_type', '')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_type': user_type,
        'search': search,
        'status': status,
        'user_types': User.USER_TYPE_CHOICES,
    }
    
    return render(request, 'admin_panel/user_management.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    """Detailed user view with edit capabilities"""
    user = get_object_or_404(User, pk=pk)
    
    # Get user profile based on type
    profile = None
    if user.user_type == 'job_seeker':
        profile = getattr(user, 'job_seeker_profile', None)
    elif user.user_type == 'employer':
        profile = getattr(user, 'employer_profile', None)
    
    # Get user activity statistics
    stats = {}
    if user.user_type == 'job_seeker' and profile:
        stats = {
            'applications': JobApplication.objects.filter(applicant=profile).count(),
            'saved_jobs': SavedJob.objects.filter(user=profile).count(),
            'profile_completeness': profile.calculate_profile_completeness(),
        }
    elif user.user_type == 'employer' and profile:
        stats = {
            'posted_jobs': Job.objects.filter(company=profile).count(),
            'active_jobs': Job.objects.filter(company=profile, status='active').count(),
            'total_applications': JobApplication.objects.filter(job__company=profile).count(),
        }
    
    context = {
        'user': user,
        'profile': profile,
        'stats': stats,
    }
    
    return render(request, 'admin_panel/user_detail.html', context)

# Job Management
@login_required
@user_passes_test(is_staff_or_admin)
def job_management(request):
    """Job management interface"""
    
    # Filters
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    jobs = Job.objects.select_related('company', 'category').order_by('-created_at')
    
    if status:
        jobs = jobs.filter(status=status)
    
    if category:
        jobs = jobs.filter(category_id=category)
    
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company__company_name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = JobCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'status': status,
        'category': category,
        'search': search,
        'job_statuses': Job.STATUS_CHOICES,
        'categories': categories,
    }
    
    return render(request, 'admin_panel/job_management.html', context)

# Analytics Views
@login_required
@user_passes_test(is_staff_or_admin)
def analytics_dashboard(request):
    """Advanced analytics dashboard"""
    
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # User Growth Analytics
    user_growth = []
    for i in range(days):
        day = timezone.now() - timedelta(days=i)
        daily_users = User.objects.filter(date_joined__date=day.date()).count()
        cumulative_users = User.objects.filter(date_joined__lte=day).count()
        user_growth.append({
            'date': day.strftime('%Y-%m-%d'),
            'daily': daily_users,
            'cumulative': cumulative_users
        })
    user_growth.reverse()
    
    # Job Application Success Rate
    total_apps = JobApplication.objects.count()
    successful_apps = JobApplication.objects.filter(status='accepted').count()
    success_rate = (successful_apps / total_apps * 100) if total_apps > 0 else 0
    
    # Most Popular Job Categories
    category_stats = JobCategory.objects.annotate(
        total_jobs=Count('job'),
        active_jobs=Count('job', filter=Q(job__status='active')),
        total_applications=Count('job__applications')
    ).order_by('-total_jobs')
    
    # Company Performance
    company_stats = EmployerProfile.objects.annotate(
        total_jobs=Count('jobs'),
        total_applications=Count('jobs__applications'),
        avg_applications_per_job=Avg('jobs__applications')
    ).order_by('-total_applications')[:10]
    
    # Application Timeline
    application_timeline = []
    for i in range(30):
        day = timezone.now() - timedelta(days=i)
        daily_apps = JobApplication.objects.filter(applied_date__date=day.date()).count()
        application_timeline.append({
            'date': day.strftime('%Y-%m-%d'),
            'applications': daily_apps
        })
    application_timeline.reverse()
    
    context = {
        'user_growth': user_growth,
        'success_rate': round(success_rate, 2),
        'category_stats': category_stats,
        'company_stats': company_stats,
        'application_timeline': application_timeline,
        'days': days,
    }
    
    return render(request, 'admin_panel/analytics.html', context)

# System Settings
@login_required
@user_passes_test(is_admin)
def system_settings(request):
    """System settings and configuration"""
    
    if request.method == 'POST':
        # Handle settings updates here
        messages.success(request, 'Settings updated successfully!')
        return redirect('admin_panel:system_settings')
    
    # Get system statistics
    system_stats = {
        'total_users': User.objects.count(),
        'total_jobs': Job.objects.count(),
        'total_applications': JobApplication.objects.count(),
        'database_size': 'N/A',  # You can implement this
        'last_backup': 'N/A',    # You can implement this
    }
    
    context = {
        'system_stats': system_stats,
    }
    
    return render(request, 'admin_panel/settings.html', context)

# AJAX Endpoints
@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_user_status(request, pk):
    """Toggle user active status"""
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully.'
    })

@login_required
@user_passes_test(is_staff_or_admin)
@require_POST
def update_job_status(request, pk):
    """Update job status"""
    job = get_object_or_404(Job, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in [choice[0] for choice in Job.STATUS_CHOICES]:
        job.status = new_status
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Job status updated to {job.get_status_display()}.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid status.'})

# Export Functions
@login_required
@user_passes_test(is_admin)
def export_users(request):
    """Export users to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'User Type', 'Date Joined', 'Is Active'])
    
    users = User.objects.all().values_list(
        'id', 'username', 'email', 'user_type', 'date_joined', 'is_active'
    )
    
    for user in users:
        writer.writerow(user)
    
    return response

@login_required
@user_passes_test(is_staff_or_admin)
def export_jobs(request):
    """Export jobs to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobs_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Title', 'Company', 'Category', 'Status', 'Created Date', 'Applications Count'])
    
    jobs = Job.objects.select_related('company', 'category').annotate(
        app_count=Count('applications')
    )
    
    for job in jobs:
        writer.writerow([
            job.id,
            job.title,
            job.company.company_name,
            job.category.name if job.category else 'N/A',
            job.status,
            job.created_at.strftime('%Y-%m-%d'),
            job.app_count
        ])
    
    return response

# Quick Stats API for Dashboard Widgets
@login_required
@user_passes_test(is_staff_or_admin)
def quick_stats_api(request):
    """API endpoint for dashboard widgets"""
    
    stats = {
        'users_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
        'jobs_today': Job.objects.filter(created_at__date=timezone.now().date()).count(),
        'applications_today': JobApplication.objects.filter(applied_date__date=timezone.now().date()).count(),
        'pending_applications': JobApplication.objects.filter(status='pending').count(),
    }
    
    return JsonResponse(stats)
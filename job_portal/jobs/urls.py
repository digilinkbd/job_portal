# jobs/urls.py - Enhanced URLs with complete job application functionality

from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public job views
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    
    # Job application views (Job Seekers)
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:pk>/apply/quick/', views.quick_apply, name='quick_apply'),
    path('job/<int:pk>/save/', views.save_job, name='save_job'),
    
    # Job seeker application management
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    
    # Employer job management views
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/jobs/', views.employer_jobs, name='employer_jobs'),
    path('employer/job/create/', views.create_job, name='create_job'),
    path('employer/job/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('employer/job/<int:pk>/delete/', views.delete_job, name='delete_job'),
    
    # Employer application management
    path('employer/job/<int:job_pk>/applications/', views.job_applications, name='job_applications'),
    path('employer/application/<int:pk>/', views.application_detail_employer, name='application_detail_employer'),
    path('employer/applications/bulk-update/', views.bulk_update_applications, name='bulk_update_applications'),
    
    # AJAX endpoints
    path('api/job/<int:pk>/quick-apply/', views.quick_apply, name='quick_apply_api'),
    path('api/job/<int:pk>/save/', views.save_job, name='save_job_api'),
    
    # Additional utility views
    path('categories/', views.job_categories, name='job_categories'),
    path('category/<int:pk>/', views.jobs_by_category, name='jobs_by_category'),
    path('company/<int:pk>/jobs/', views.jobs_by_company, name='jobs_by_company'),
]
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Public job views
    path('', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    
    # Employer views
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/jobs/', views.employer_jobs, name='employer_jobs'),
    path('employer/job/create/', views.create_job, name='create_job'),
    path('employer/job/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('employer/job/<int:pk>/delete/', views.delete_job, name='delete_job'),
    
    # Job seeker views
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:pk>/save/', views.save_job, name='save_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
]
# admin_panel/urls.py - Custom Admin Panel URL Configuration

from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Main Admin Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Job Management
    path('jobs/', views.job_management, name='job_management'),
    path('jobs/<int:pk>/update-status/', views.update_job_status, name='update_job_status'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
    
    # Export Functions
    path('export/users/', views.export_users, name='export_users'),
    path('export/jobs/', views.export_jobs, name='export_jobs'),
    
    # API Endpoints
    path('api/quick-stats/', views.quick_stats_api, name='quick_stats_api'),
]
# accounts/urls.py - URL Configuration for Authentication

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Registration URLs
    path('register/', views.register_choice, name='register_choice'),
    path('register/job-seeker/', views.job_seeker_register, name='job_seeker_register'),
    path('register/employer/', views.employer_register, name='employer_register'),
    
    # Dashboard URLs
    path('dashboard/job-seeker/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
    path('dashboard/employer/', views.employer_dashboard, name='employer_dashboard'),
    
    # Profile Setup URLs (for new users)
    path('setup/job-seeker/', views.job_seeker_profile_setup, name='job_seeker_profile_setup'),
    path('setup/employer/', views.employer_profile_setup, name='employer_profile_setup'),
    
    # Profile Management URLs
    path('profile/job-seeker/', views.job_seeker_profile, name='job_seeker_profile'),
    path('profile/employer/', views.employer_profile, name='employer_profile'),
    
    # Public Profile URLs
    path('profile/job-seeker/<int:pk>/', views.job_seeker_public_profile, name='job_seeker_profile_public'),
    path('profile/employer/<int:pk>/', views.employer_public_profile, name='employer_profile_public'),
    
    # Account Settings
    path('settings/', views.account_settings, name='account_settings'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # AJAX URLs
    path('api/profile-completeness/', views.check_profile_completeness, name='check_profile_completeness'),
    
    # Password Reset URLs (using Django's built-in views)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset-done/'
         ),
         name='password_reset'),
    
    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Password Change URLs (for authenticated users)
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change.html',
             success_url='/accounts/password-change-done/'
         ),
         name='password_change'),
    
    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ),
         name='password_change_done'),
]
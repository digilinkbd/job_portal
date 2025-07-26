# accounts/admin.py - Corrected to match your actual model fields

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, JobSeekerProfile, EmployerProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_email_verified', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'is_email_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'email', 'first_name', 'last_name')}),
    )

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_full_name', 'experience_level', 'city', 'is_profile_complete', 'created_at']
    list_filter = ['experience_level', 'city', 'state', 'country', 'is_profile_complete', 'profile_visibility', 'created_at']
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name', 'skills', 'current_company']
    readonly_fields = ['created_at', 'updated_at', 'get_profile_completeness']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'profile_picture', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Professional Information', {
            'fields': ('headline', 'bio', 'experience_level', 'current_position', 'current_company')
        }),
        ('Skills & Preferences', {
            'fields': ('skills', 'desired_job_types', 'desired_salary_min', 'desired_salary_max', 
                      'preferred_locations', 'willing_to_relocate', 'open_to_remote')
        }),
        ('Documents', {
            'fields': ('resume', 'cover_letter_template')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'portfolio_url')
        }),
        ('Settings', {
            'fields': ('profile_visibility', 'is_profile_complete', 'get_profile_completeness')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_profile_completeness(self, obj):
        return f"{obj.calculate_profile_completeness()}%"
    get_profile_completeness.short_description = 'Profile Completeness'

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'contact_person', 'city', 'industry', 'is_verified', 'created_at']
    list_filter = ['industry', 'company_size', 'city', 'state', 'country', 'is_verified', 'created_at']
    search_fields = ['company_name', 'user__username', 'user__email', 'contact_person', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_profile_completeness']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_logo', 'description', 'industry', 'company_size', 'founded_year')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_email', 'phone')
        }),
        ('Location', {
            'fields': ('headquarters', 'address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Online Presence', {
            'fields': ('website', 'linkedin_url', 'twitter_url', 'facebook_url')
        }),
        ('Company Details', {
            'fields': ('mission_statement', 'benefits_offered', 'work_culture')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_document')
        }),
        ('Settings', {
            'fields': ('is_profile_complete', 'get_profile_completeness')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_profile_completeness(self, obj):
        return f"{obj.calculate_profile_completeness()}%"
    get_profile_completeness.short_description = 'Profile Completeness'
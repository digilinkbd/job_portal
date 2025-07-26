# admin_panel/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import JobSeekerProfile, EmployerProfile

# Get the User model from accounts app
User = get_user_model()

class JobSeekerProfileInline(admin.StackedInline):
    model = JobSeekerProfile
    can_delete = False
    verbose_name_plural = 'Job Seeker Profile'
    fields = (
        'phone', 'location', 'job_title', 'experience_level', 
        'salary_expectation', 'employment_type', 'remote_work',
        'linkedin_url', 'portfolio_url', 'github_url',
        'profile_visibility', 'email_notifications'
    )

class EmployerProfileInline(admin.StackedInline):
    model = EmployerProfile
    can_delete = False
    verbose_name_plural = 'Employer Profile'
    fields = (
        'company_name', 'company_size', 'industry', 'phone',
        'website', 'location', 'description', 'benefits',
        'linkedin_url', 'twitter_url', 'facebook_url'
    )

# Only register UserAdmin if it's not already registered by accounts app
# Check if User is already registered
if not admin.site.is_registered(User):
    @admin.register(User)
    class UserAdmin(BaseUserAdmin):
        list_display = ('username', 'email', 'user_type', 'is_active', 'date_joined', 'profile_status')
        list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
        search_fields = ('username', 'email', 'first_name', 'last_name')
        ordering = ('-date_joined',)
        
        fieldsets = BaseUserAdmin.fieldsets + (
            ('User Type', {'fields': ('user_type',)}),
        )
        
        def profile_status(self, obj):
            if obj.user_type == 'job_seeker':
                try:
                    profile = obj.jobseekerprofile
                    return format_html('<span style="color: green;">✓ Complete</span>')
                except JobSeekerProfile.DoesNotExist:
                    return format_html('<span style="color: red;">✗ Incomplete</span>')
            elif obj.user_type == 'employer':
                try:
                    profile = obj.employerprofile
                    return format_html('<span style="color: green;">✓ Complete</span>')
                except EmployerProfile.DoesNotExist:
                    return format_html('<span style="color: red;">✗ Incomplete</span>')
            return '-'
        
        profile_status.short_description = 'Profile Status'
        
        def get_inlines(self, request, obj):
            if obj and obj.user_type == 'job_seeker':
                return [JobSeekerProfileInline]
            elif obj and obj.user_type == 'employer':
                return [EmployerProfileInline]
            return []

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'experience_level', 'location', 'profile_visibility', 'created_at')
    list_filter = ('experience_level', 'employment_type', 'remote_work', 'profile_visibility', 'created_at')
    search_fields = ('user__username', 'user__email', 'job_title', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('phone', 'location')
        }),
        ('Professional Information', {
            'fields': ('job_title', 'bio', 'skills', 'experience_level', 'experience_details')
        }),
        ('Job Preferences', {
            'fields': ('salary_expectation', 'employment_type', 'remote_work', 'availability')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'portfolio_url', 'github_url'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('profile_visibility', 'email_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'industry', 'company_size', 'location', 'created_at')
    list_filter = ('company_size', 'industry', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': ('company_name', 'company_size', 'industry', 'website')
        }),
        ('Contact Information', {
            'fields': ('phone', 'location')
        }),
        ('Company Profile', {
            'fields': ('description', 'benefits')
        }),
        ('Social Media', {
            'fields': ('linkedin_url', 'twitter_url', 'facebook_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site header and title
admin.site.site_header = "Job Portal Admin"
admin.site.site_title = "Job Portal Admin"
admin.site.index_title = "Welcome to Job Portal Administration"

from django.contrib import admin
from django.utils.html import format_html
from .models import JobCategory, Job, JobApplication, SavedJob

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'jobs_count', 'created_at']
    search_fields = ['name']
    
    def jobs_count(self, obj):
        return obj.jobs.count()
    jobs_count.short_description = 'Number of Jobs'

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'category', 'job_type', 'status', 
        'created_at', 'applications_count', 'views_count'
    ]
    list_filter = [
        'status', 'job_type', 'experience_level', 'category', 
        'is_remote', 'created_at'
    ]
    search_fields = [
        'title', 'company__company_name', 'description', 
        'required_skills', 'location'
    ]
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'category', 'status')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities')
        }),
        ('Job Specifications', {
            'fields': ('job_type', 'experience_level', 'deadline')
        }),
        ('Location & Remote', {
            'fields': ('location', 'is_remote')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'salary_currency')
        }),
        ('Skills', {
            'fields': ('required_skills', 'preferred_skills')
        }),
        ('Metadata', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def applications_count(self, obj):
        count = obj.applications.count()
        if count > 0:
            return format_html(
                '<a href="/admin/jobs/jobapplication/?job__id__exact={}">{} applications</a>',
                obj.pk, count
            )
        return "0 applications"
    applications_count.short_description = 'Applications'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant_name', 'job_title', 'company_name', 'status', 
        'applied_date', 'has_resume'
    ]
    list_filter = ['status', 'applied_date', 'job__job_type']
    search_fields = [
        'applicant__user__username', 'applicant__user__email',
        'job__title', 'job__company__company_name'
    ]
    readonly_fields = ['applied_date', 'updated_date']
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume')
        }),
        ('Employer Notes', {
            'fields': ('employer_notes',)
        }),
        ('Timestamps', {
            'fields': ('applied_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def applicant_name(self, obj):
        return obj.applicant.user.get_full_name() or obj.applicant.user.username
    applicant_name.short_description = 'Applicant'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'
    
    def company_name(self, obj):
        return obj.job.company.company_name
    company_name.short_description = 'Company'
    
    def has_resume(self, obj):
        return "Yes" if obj.resume else "No"
    has_resume.short_description = 'Resume Uploaded'
    has_resume.boolean = True

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'job_title', 'company_name', 'saved_date']
    list_filter = ['saved_date']
    search_fields = [
        'user__user__username', 'job__title', 'job__company__company_name'
    ]
    
    def user_name(self, obj):
        return obj.user.user.get_full_name() or obj.user.user.username
    user_name.short_description = 'User'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'
    
    def company_name(self, obj):
        return obj.job.company.company_name
    company_name.short_description = 'Company'


class MathFilterAdmin(admin.ModelAdmin):
    list_display = ['filter_name', 'description']
    search_fields = ['filter_name', 'description']
    
    def filter_name(self, obj):
        return obj.name
    filter_name.short_description = 'Filter Name'
    
    def description(self, obj):
        return obj.description
    description.short_description = 'Description'
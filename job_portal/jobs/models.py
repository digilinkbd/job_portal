from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Job Categories"
    
    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-1 years)'),
        ('junior', 'Junior (1-3 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior (5-8 years)'),
        ('lead', 'Lead/Principal (8+ years)'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    company = models.ForeignKey('accounts.EmployerProfile', on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Job Details
    description = models.TextField()
    requirements = models.TextField(help_text="Job requirements and qualifications")
    responsibilities = models.TextField(help_text="Key responsibilities")
    
    # Job Specifications
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    
    # Location and Salary
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum salary")
    salary_max = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum salary")
    salary_currency = models.CharField(max_length=10, default='USD')
    
    # Skills and Tags
    required_skills = models.TextField(blank=True, help_text="Comma-separated required skills")
    preferred_skills = models.TextField(blank=True, help_text="Comma-separated preferred skills")
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    deadline = models.DateField(null=True, blank=True, help_text="Application deadline")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company.company_name}"
    
    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'pk': self.pk})
    
    def get_required_skills_list(self):
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',')]
        return []
    
    def get_preferred_skills_list(self):
        if self.preferred_skills:
            return [skill.strip() for skill in self.preferred_skills.split(',')]
        return []
    
    def get_salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,}+"
        return "Salary not specified"
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey('accounts.JobSeekerProfile', on_delete=models.CASCADE, related_name='applications')
    
    # Application Details
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    # Employer Notes
    employer_notes = models.TextField(blank=True, help_text="Internal notes for employer")
    
    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.applicant.user.username} applied for {self.job.title}"

class SavedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey('accounts.JobSeekerProfile', on_delete=models.CASCADE, related_name='saved_jobs')
    saved_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['job', 'user']
        ordering = ['-saved_date']
    
    def __str__(self):
        return f"{self.user.user.username} saved {self.job.title}"
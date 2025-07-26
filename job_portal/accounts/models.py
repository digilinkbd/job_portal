# accounts/models.py - Complete User Authentication Models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from PIL import Image
import os

class User(AbstractUser):
    """Custom User model with role-based authentication"""
    
    USER_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    def get_absolute_url(self):
        if self.user_type == 'job_seeker':
            return reverse('accounts:job_seeker_profile')
        elif self.user_type == 'employer':
            return reverse('accounts:employer_profile')
        return reverse('accounts:profile')

class JobSeekerProfile(models.Model):
    """Profile for job seekers"""
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-1 years)'),
        ('junior', 'Junior (1-3 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior (5-8 years)'),
        ('lead', 'Lead/Principal (8+ years)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='profile_pics/job_seekers/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional Information
    headline = models.CharField(max_length=200, blank=True, help_text="Professional headline/title")
    bio = models.TextField(blank=True, help_text="Brief professional summary")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='entry')
    current_position = models.CharField(max_length=200, blank=True)
    current_company = models.CharField(max_length=200, blank=True)
    
    # Skills and Preferences
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    desired_job_types = models.CharField(max_length=200, blank=True, help_text="Comma-separated job types")
    desired_salary_min = models.PositiveIntegerField(blank=True, null=True)
    desired_salary_max = models.PositiveIntegerField(blank=True, null=True)
    preferred_locations = models.TextField(blank=True, help_text="Comma-separated preferred locations")
    willing_to_relocate = models.BooleanField(default=False)
    open_to_remote = models.BooleanField(default=True)
    
    # Documents
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter_template = models.TextField(blank=True, help_text="Default cover letter template")
    
    # Social Links
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Privacy Settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('private', 'Private'), ('employers_only', 'Employers Only')],
        default='employers_only'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_profile_complete = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_full_name()} - Job Seeker"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_skills_list(self):
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
    def get_desired_job_types_list(self):
        if self.desired_job_types:
            return [job_type.strip() for job_type in self.desired_job_types.split(',')]
        return []
    
    def get_preferred_locations_list(self):
        if self.preferred_locations:
            return [location.strip() for location in self.preferred_locations.split(',')]
        return []
    
    def calculate_profile_completeness(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'first_name', 'last_name', 'phone', 'headline', 'bio',
            'experience_level', 'skills', 'resume'
        ]
        completed_fields = sum(1 for field in fields_to_check if getattr(self, field))
        return int((completed_fields / len(fields_to_check)) * 100)
    
    def save(self, *args, **kwargs):
        # Update profile completeness
        self.is_profile_complete = self.calculate_profile_completeness() >= 70
        
        super().save(*args, **kwargs)
        
        # Resize profile picture
        if self.profile_picture:
            self.resize_image()
    
    def resize_image(self):
        """Resize profile picture to optimize storage"""
        if self.profile_picture:
            image_path = self.profile_picture.path
            if os.path.exists(image_path):
                with Image.open(image_path) as img:
                    if img.height > 300 or img.width > 300:
                        img.thumbnail((300, 300))
                        img.save(image_path, optimize=True, quality=85)

class EmployerProfile(models.Model):
    """Profile for employers/companies"""
    
    COMPANY_SIZES = [
        ('startup', 'Startup (1-10 employees)'),
        ('small', 'Small (11-50 employees)'),
        ('medium', 'Medium (51-200 employees)'),
        ('large', 'Large (201-1000 employees)'),
        ('enterprise', 'Enterprise (1000+ employees)'),
    ]
    
    INDUSTRIES = [
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('media', 'Media & Entertainment'),
        ('nonprofit', 'Non-Profit'),
        ('government', 'Government'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    
    # Company Information
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(help_text="Company description and culture")
    industry = models.CharField(max_length=50, choices=INDUSTRIES, blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES, blank=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Contact Information
    contact_person = models.CharField(max_length=100, help_text="HR/Hiring manager name")
    contact_email = models.EmailField(help_text="Hiring contact email")
    phone = models.CharField(max_length=20, blank=True)
    
    # Location
    headquarters = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Online Presence
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    
    # Company Details
    mission_statement = models.TextField(blank=True)
    benefits_offered = models.TextField(blank=True, help_text="Employee benefits and perks")
    work_culture = models.TextField(blank=True, help_text="Description of work culture and values")
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_profile_complete = models.BooleanField(default=False)
    
    def __str__(self):
        return self.company_name
    
    def get_absolute_url(self):
        return reverse('accounts:employer_profile_public', kwargs={'pk': self.pk})
    
    def calculate_profile_completeness(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'company_name', 'description', 'industry', 'company_size',
            'contact_person', 'contact_email', 'website', 'headquarters'
        ]
        completed_fields = sum(1 for field in fields_to_check if getattr(self, field))
        return int((completed_fields / len(fields_to_check)) * 100)
    
    def save(self, *args, **kwargs):
        # Update profile completeness
        self.is_profile_complete = self.calculate_profile_completeness() >= 70
        
        super().save(*args, **kwargs)
        
        # Resize company logo
        if self.company_logo:
            self.resize_logo()
    
    def resize_logo(self):
        """Resize company logo to optimize storage"""
        if self.company_logo:
            image_path = self.company_logo.path
            if os.path.exists(image_path):
                with Image.open(image_path) as img:
                    if img.height > 200 or img.width > 200:
                        img.thumbnail((200, 200))
                        img.save(image_path, optimize=True, quality=85)

# Signal to create profiles automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create user profile based on user type"""
    if created:
        if instance.user_type == 'job_seeker':
            JobSeekerProfile.objects.create(user=instance)
        elif instance.user_type == 'employer':
            EmployerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if instance.user_type == 'job_seeker' and hasattr(instance, 'job_seeker_profile'):
        instance.job_seeker_profile.save()
    elif instance.user_type == 'employer' and hasattr(instance, 'employer_profile'):
        instance.employer_profile.save()
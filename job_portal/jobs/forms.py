# jobs/forms.py - Add these forms to your existing jobs/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Job, JobApplication, JobCategory
import os

class JobApplicationForm(forms.ModelForm):
    """Form for job applications"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write a compelling cover letter explaining why you are the perfect fit for this position...'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }
    
    def __init__(self, *args, job=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = job
        self.user = user
        
        # Pre-populate cover letter if user has a template
        if user and hasattr(user, 'job_seeker_profile') and user.job_seeker_profile.cover_letter_template:
            if not self.instance.pk:  # Only for new applications
                template = user.job_seeker_profile.cover_letter_template
                # Replace placeholders with actual job details
                if job:
                    template = template.replace('[COMPANY_NAME]', job.company.company_name)
                    template = template.replace('[JOB_TITLE]', job.title)
                    template = template.replace('[HIRING_MANAGER]', job.company.contact_person or 'Hiring Manager')
                
                self.fields['cover_letter'].initial = template
        
        # Make resume optional if user has one in their profile
        if user and hasattr(user, 'job_seeker_profile') and user.job_seeker_profile.resume:
            self.fields['resume'].required = False
            self.fields['resume'].help_text = f'Optional: Leave blank to use your profile resume ({os.path.basename(user.job_seeker_profile.resume.name)})'
        
        # Add labels
        self.fields['cover_letter'].label = 'Cover Letter'
        self.fields['resume'].label = 'Resume (PDF, DOC, DOCX only)'
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        
        if resume:
            # Check file size (5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise ValidationError('Resume file size cannot exceed 5MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = os.path.splitext(resume.name)[1].lower()
            
            if file_extension not in allowed_extensions:
                raise ValidationError('Only PDF, DOC, and DOCX files are allowed.')
        
        return resume
    
    def clean(self):
        cleaned_data = super().clean()
        resume = cleaned_data.get('resume')
        
        # If no resume provided, check if user has one in profile
        if not resume and self.user:
            if hasattr(self.user, 'job_seeker_profile') and self.user.job_seeker_profile.resume:
                # User can use profile resume
                pass
            else:
                raise ValidationError('Please upload a resume or add one to your profile.')
        
        return cleaned_data

class JobSearchForm(forms.Form):
    """Enhanced job search form"""
    
    search = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title, company, or keywords...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    location = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, state, or country...'
        })
    )
    
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Job.EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    salary_min = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum salary...'
        })
    )
    
    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-salary_min', 'Highest Salary'),
            ('salary_min', 'Lowest Salary'),
            ('-views_count', 'Most Popular'),
            ('title', 'Job Title A-Z'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class ApplicationStatusForm(forms.ModelForm):
    """Form for employers to update application status"""
    
    class Meta:
        model = JobApplication
        fields = ['status', 'employer_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'employer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Internal notes about this application...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].label = 'Application Status'
        self.fields['employer_notes'].label = 'Internal Notes'

class JobForm(forms.ModelForm):
    """Enhanced job creation/editing form"""
    
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'responsibilities', 'requirements',
            'job_type', 'experience_level', 'location', 'is_remote',
            'salary_min', 'salary_max', 'salary_currency',
            'required_skills', 'preferred_skills', 'deadline', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_currency': forms.TextInput(attrs={'class': 'form-control'}),
            'required_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Python, JavaScript, React, etc.'
            }),
            'preferred_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Docker, AWS, GraphQL, etc.'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise ValidationError('Minimum salary cannot be higher than maximum salary.')
        
        return cleaned_data

class BulkJobActionForm(forms.Form):
    """Form for bulk actions on jobs"""
    
    ACTION_CHOICES = [
        ('activate', 'Activate Selected Jobs'),
        ('pause', 'Pause Selected Jobs'),
        ('close', 'Close Selected Jobs'),
        ('delete', 'Delete Selected Jobs'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    job_ids = forms.CharField(widget=forms.HiddenInput())
    
    def clean_job_ids(self):
        job_ids = self.cleaned_data['job_ids']
        if not job_ids:
            raise ValidationError('Please select at least one job.')
        
        try:
            job_id_list = [int(id.strip()) for id in job_ids.split(',') if id.strip()]
            return job_id_list
        except ValueError:
            raise ValidationError('Invalid job selection.')

class QuickApplyForm(forms.Form):
    """Quick apply form for jobs"""
    
    cover_letter = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Optional: Brief message to the employer...'
        })
    )
    
    use_profile_resume = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'job_seeker_profile'):
            profile = user.job_seeker_profile
            if profile.resume:
                self.fields['use_profile_resume'].label = f'Use my profile resume ({os.path.basename(profile.resume.name)})'
            else:
                # If no profile resume, remove the checkbox and make it required to upload
                del self.fields['use_profile_resume']
                self.fields['resume'] = forms.FileField(
                    required=True,
                    widget=forms.FileInput(attrs={
                        'class': 'form-control',
                        'accept': '.pdf,.doc,.docx'
                    })
                )
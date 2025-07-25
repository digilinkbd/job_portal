from django import forms
from django.core.exceptions import ValidationError
from .models import Job, JobCategory, JobApplication

class JobForm(forms.ModelForm):
    required_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., Python, Django, JavaScript, SQL'}),
        help_text="Enter required skills separated by commas",
        required=False
    )
    
    preferred_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., React, AWS, Docker'}),
        help_text="Enter preferred skills separated by commas",
        required=False
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'requirements', 'responsibilities',
            'job_type', 'experience_level', 'location', 'is_remote',
            'salary_min', 'salary_max', 'salary_currency',
            'required_skills', 'preferred_skills', 'deadline', 'status'
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., New York, NY or Remote'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['requirements'].required = True
        self.fields['location'].required = True
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max:
            if salary_min >= salary_max:
                raise ValidationError("Maximum salary must be greater than minimum salary.")
        
        return cleaned_data

class JobSearchForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
        ('-views_count', 'Most Popular'),
    ]
    
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search jobs by title, company, or skills...',
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Job.EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter location...',
            'class': 'form-control'
        })
    )
    
    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    salary_min = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min salary',
            'class': 'form-control'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_sort_by(self):
        """Ensure sort_by has a valid value"""
        sort_by = self.cleaned_data.get('sort_by')
        if not sort_by:
            return '-created_at'
        return sort_by

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write a compelling cover letter explaining why you are the perfect fit for this role...',
                'class': 'form-control'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_letter'].required = True
        self.fields['resume'].help_text = "Upload your resume (PDF, DOC, DOCX only)"

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status', 'employer_notes']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'employer_notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Add internal notes about this application...',
                'class': 'form-control'
            })
        }

class JobCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = ['name', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }
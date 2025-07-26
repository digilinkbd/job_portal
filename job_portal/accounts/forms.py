# accounts/forms.py - Fixed Authentication and Profile Forms

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, JobSeekerProfile, EmployerProfile

class JobSeekerRegistrationForm(UserCreationForm):
    """Registration form for job seekers with additional fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.user_type = 'job_seeker'
        
        if commit:
            user.save()
            # Create or update job seeker profile
            profile, created = JobSeekerProfile.objects.get_or_create(user=user)
            profile.first_name = self.cleaned_data['first_name']
            profile.last_name = self.cleaned_data['last_name']
            profile.save()
        
        return user

class EmployerRegistrationForm(UserCreationForm):
    """Registration form for employers with company details"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    company_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name'
        })
    )
    contact_person = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact person name'
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'company_name', 'contact_person', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.user_type = 'employer'
        
        if commit:
            user.save()
            # Create or update employer profile
            profile, created = EmployerProfile.objects.get_or_create(user=user)
            profile.company_name = self.cleaned_data['company_name']
            profile.contact_person = self.cleaned_data['contact_person']
            profile.contact_email = self.cleaned_data['email']
            profile.save()
        
        return user

class CustomLoginForm(AuthenticationForm):
    """Custom login form with email support"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email or Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with email first, then username
            user = None
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(self.request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                user = authenticate(self.request, username=username, password=password)
            
            if not user:
                raise forms.ValidationError("Invalid email/username or password.")
            
            self.user_cache = user
        
        return self.cleaned_data

class JobSeekerProfileForm(forms.ModelForm):
    """Form for updating job seeker profile"""
    
    class Meta:
        model = JobSeekerProfile
        fields = [
            'first_name', 'last_name', 'profile_picture', 'phone', 'address', 
            'city', 'state', 'country', 'postal_code', 'headline', 'bio',
            'experience_level', 'current_position', 'current_company', 'skills',
            'desired_job_types', 'desired_salary_min', 'desired_salary_max',
            'preferred_locations', 'willing_to_relocate', 'open_to_remote',
            'resume', 'linkedin_url', 'github_url', 'portfolio_url',
            'profile_visibility'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief professional summary...'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, JavaScript, React, etc.'}),
            'desired_job_types': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full-time, Remote, Contract'}),
            'desired_salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'desired_salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'preferred_locations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'New York, San Francisco, Remote'}),
            'willing_to_relocate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'open_to_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
            'profile_visibility': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployerProfileForm(forms.ModelForm):
    """Form for updating employer profile"""
    
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name', 'company_logo', 'description', 'industry', 
            'company_size', 'founded_year', 'contact_person', 'contact_email',
            'phone', 'headquarters', 'address', 'city', 'state', 'country',
            'postal_code', 'website', 'linkedin_url', 'twitter_url', 
            'facebook_url', 'mission_statement', 'benefits_offered', 'work_culture'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'headquarters': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'mission_statement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'benefits_offered': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'work_culture': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
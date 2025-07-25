from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, JobSeekerProfile, EmployerProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=False)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, widget=forms.RadioSelect)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'user_type', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
            # Create corresponding profile based on user type
            if user.user_type == 'job_seeker':
                JobSeekerProfile.objects.create(user=user)
            elif user.user_type == 'employer':
                EmployerProfile.objects.create(user=user, company_name=f"{user.first_name}'s Company")
                
        return user

class JobSeekerProfileForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., Python, Django, JavaScript'}),
        help_text="Enter your skills separated by commas"
    )
    
    class Meta:
        model = JobSeekerProfile
        fields = ['resume', 'skills', 'experience_years', 'location', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_description', 'website', 'location', 'company_logo']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive")
        
        return self.cleaned_data
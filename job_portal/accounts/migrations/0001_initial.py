# Generated by Django 5.2.4 on 2025-07-26 10:25

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user_type', models.CharField(choices=[('job_seeker', 'Job Seeker'), ('employer', 'Employer'), ('admin', 'Admin')], max_length=20)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='EmployerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('description', models.TextField(help_text='Company description and culture')),
                ('industry', models.CharField(blank=True, choices=[('technology', 'Technology'), ('healthcare', 'Healthcare'), ('finance', 'Finance'), ('education', 'Education'), ('retail', 'Retail'), ('manufacturing', 'Manufacturing'), ('consulting', 'Consulting'), ('media', 'Media & Entertainment'), ('nonprofit', 'Non-Profit'), ('government', 'Government'), ('other', 'Other')], max_length=50)),
                ('company_size', models.CharField(blank=True, choices=[('startup', 'Startup (1-10 employees)'), ('small', 'Small (11-50 employees)'), ('medium', 'Medium (51-200 employees)'), ('large', 'Large (201-1000 employees)'), ('enterprise', 'Enterprise (1000+ employees)')], max_length=20)),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True)),
                ('contact_person', models.CharField(help_text='HR/Hiring manager name', max_length=100)),
                ('contact_email', models.EmailField(help_text='Hiring contact email', max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('headquarters', models.CharField(blank=True, max_length=200)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('website', models.URLField(blank=True)),
                ('linkedin_url', models.URLField(blank=True)),
                ('twitter_url', models.URLField(blank=True)),
                ('facebook_url', models.URLField(blank=True)),
                ('mission_statement', models.TextField(blank=True)),
                ('benefits_offered', models.TextField(blank=True, help_text='Employee benefits and perks')),
                ('work_culture', models.TextField(blank=True, help_text='Description of work culture and values')),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_document', models.FileField(blank=True, null=True, upload_to='verification_docs/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_profile_complete', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobSeekerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/job_seekers/')),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=10)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('headline', models.CharField(blank=True, help_text='Professional headline/title', max_length=200)),
                ('bio', models.TextField(blank=True, help_text='Brief professional summary')),
                ('experience_level', models.CharField(choices=[('entry', 'Entry Level (0-1 years)'), ('junior', 'Junior (1-3 years)'), ('mid', 'Mid Level (3-5 years)'), ('senior', 'Senior (5-8 years)'), ('lead', 'Lead/Principal (8+ years)')], default='entry', max_length=20)),
                ('current_position', models.CharField(blank=True, max_length=200)),
                ('current_company', models.CharField(blank=True, max_length=200)),
                ('skills', models.TextField(blank=True, help_text='Comma-separated skills')),
                ('desired_job_types', models.CharField(blank=True, help_text='Comma-separated job types', max_length=200)),
                ('desired_salary_min', models.PositiveIntegerField(blank=True, null=True)),
                ('desired_salary_max', models.PositiveIntegerField(blank=True, null=True)),
                ('preferred_locations', models.TextField(blank=True, help_text='Comma-separated preferred locations')),
                ('willing_to_relocate', models.BooleanField(default=False)),
                ('open_to_remote', models.BooleanField(default=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('cover_letter_template', models.TextField(blank=True, help_text='Default cover letter template')),
                ('linkedin_url', models.URLField(blank=True)),
                ('github_url', models.URLField(blank=True)),
                ('portfolio_url', models.URLField(blank=True)),
                ('profile_visibility', models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('employers_only', 'Employers Only')], default='employers_only', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_profile_complete', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job_seeker_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

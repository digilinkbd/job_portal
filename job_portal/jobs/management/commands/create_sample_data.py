from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import EmployerProfile, JobSeekerProfile
from jobs.models import JobCategory, Job
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing the job portal'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create job categories
        categories_data = [
            ('Software Development', 'Programming and software engineering roles'),
            ('Data Science', 'Data analysis, machine learning, and AI roles'),
            ('Design', 'UI/UX design and graphic design positions'),
            ('Marketing', 'Digital marketing and content creation roles'),
            ('Sales', 'Business development and sales positions'),
            ('HR', 'Human resources and recruiting roles'),
        ]

        categories = {}
        for name, desc in categories_data:
            category, created = JobCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            categories[name] = category
            if created:
                self.stdout.write(f'  Created category: {name}')

        # Create sample employer
        employer_user, created = User.objects.get_or_create(
            username='techcorp_hr',
            defaults={
                'email': 'hr@techcorp.com',
                'first_name': 'Tech',
                'last_name': 'Corp HR',
                'user_type': 'employer',
                'is_active': True
            }
        )
        if created:
            employer_user.set_password('password123')
            employer_user.save()

        employer_profile, created = EmployerProfile.objects.get_or_create(
            user=employer_user,
            defaults={
                'company_name': 'TechCorp Solutions',
                'company_description': 'Leading technology solutions provider',
                'website': 'https://techcorp.com',
                'location': 'San Francisco, CA'
            }
        )
        if created:
            self.stdout.write('  Created employer: TechCorp Solutions')

        # Create sample job seeker
        seeker_user, created = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'user_type': 'job_seeker',
                'is_active': True
            }
        )
        if created:
            seeker_user.set_password('password123')
            seeker_user.save()

        seeker_profile, created = JobSeekerProfile.objects.get_or_create(
            user=seeker_user,
            defaults={
                'skills': 'Python, Django, JavaScript, React',
                'experience_years': 3,
                'location': 'New York, NY',
                'bio': 'Passionate software developer with 3 years of experience'
            }
        )
        if created:
            self.stdout.write('  Created job seeker: John Doe')

        # Create sample jobs
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'category': categories['Software Development'],
                'description': 'We are looking for an experienced Python developer to join our team.',
                'requirements': 'Bachelor degree in Computer Science, 5+ years Python experience',
                'responsibilities': 'Develop web applications, write clean code, mentor junior developers',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'San Francisco, CA',
                'is_remote': False,
                'salary_min': 120000,
                'salary_max': 160000,
                'required_skills': 'Python, Django, PostgreSQL, Redis',
                'preferred_skills': 'AWS, Docker, Kubernetes',
                'status': 'active',
                'deadline': date.today() + timedelta(days=30)
            },
            {
                'title': 'Frontend React Developer',
                'category': categories['Software Development'],
                'description': 'Join our frontend team to build amazing user interfaces.',
                'requirements': '3+ years React experience, strong JavaScript skills',
                'responsibilities': 'Build responsive UIs, optimize performance, collaborate with designers',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'location': 'Remote',
                'is_remote': True,
                'salary_min': 80000,
                'salary_max': 120000,
                'required_skills': 'React, JavaScript, HTML, CSS',
                'preferred_skills': 'TypeScript, Next.js, Tailwind CSS',
                'status': 'active',
                'deadline': date.today() + timedelta(days=25)
            },
            {
                'title': 'Data Scientist',
                'category': categories['Data Science'],
                'description': 'Analyze data and build machine learning models.',
                'requirements': 'PhD or Masters in Data Science, Python/R experience',
                'responsibilities': 'Data analysis, ML model development, reporting insights',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'location': 'New York, NY',
                'is_remote': False,
                'salary_min': 130000,
                'salary_max': 180000,
                'required_skills': 'Python, R, SQL, Machine Learning',
                'preferred_skills': 'TensorFlow, PyTorch, AWS SageMaker',
                'status': 'active',
                'deadline': date.today() + timedelta(days=20)
            },
            {
                'title': 'UX/UI Designer',
                'category': categories['Design'],
                'description': 'Create beautiful and intuitive user experiences.',
                'requirements': '3+ years design experience, portfolio required',
                'responsibilities': 'Design user interfaces, create prototypes, user research',
                'job_type': 'contract',
                'experience_level': 'mid',
                'location': 'Los Angeles, CA',
                'is_remote': True,
                'salary_min': 70000,
                'salary_max': 100000,
                'required_skills': 'Figma, Sketch, Adobe Creative Suite',
                'preferred_skills': 'Prototyping, User Research, HTML/CSS',
                'status': 'active',
                'deadline': date.today() + timedelta(days=15)
            },
            {
                'title': 'Digital Marketing Specialist',
                'category': categories['Marketing'],
                'description': 'Drive our digital marketing campaigns and growth.',
                'requirements': '2+ years digital marketing experience',
                'responsibilities': 'Manage campaigns, analyze metrics, content creation',
                'job_type': 'part_time',
                'experience_level': 'junior',
                'location': 'Austin, TX',
                'is_remote': True,
                'salary_min': 45000,
                'salary_max': 65000,
                'required_skills': 'Google Ads, Facebook Ads, Analytics',
                'preferred_skills': 'SEO, Content Marketing, Email Marketing',
                'status': 'active',
                'deadline': date.today() + timedelta(days=10)
            }
        ]

        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=employer_profile,
                defaults=job_data
            )
            if created:
                self.stdout.write(f'  Created job: {job_data["title"]}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('Sample login credentials:')
        self.stdout.write('  Employer: username=techcorp_hr, password=password123')
        self.stdout.write('  Job Seeker: username=john_doe, password=password123')
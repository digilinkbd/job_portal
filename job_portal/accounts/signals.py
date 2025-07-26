# accounts/signals.py - User Profile Creation Signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeekerProfile, EmployerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create user profile based on user type"""
    if created:
        if instance.user_type == 'job_seeker':
            JobSeekerProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'employer':
            EmployerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if instance.user_type == 'job_seeker':
        profile, created = JobSeekerProfile.objects.get_or_create(user=instance)
        if not created:
            profile.save()
    elif instance.user_type == 'employer':
        profile, created = EmployerProfile.objects.get_or_create(user=instance)
        if not created:
            profile.save()
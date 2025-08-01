# accounts/apps.py - Fixed App Configuration

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        # Import signals to ensure they are registered
        import accounts.signals
import sys
import os

# Full path to your Django project directory
sys.path.insert(0, os.path.dirname(__file__))

# Replace 'your_project_name' with your actual settings module path (folder name)
os.environ['DJANGO_SETTINGS_MODULE'] = 'job_portal.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

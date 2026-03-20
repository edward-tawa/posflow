import os
from celery import Celery

# set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posflow.settings')

app = Celery('posflow')

# Load config from Django settings, using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()
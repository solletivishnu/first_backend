# project_name/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tara.settings.default')

app = Celery('Tara')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

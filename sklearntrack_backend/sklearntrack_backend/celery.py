import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sklearntrack_backend.settings')

app = Celery('sklearntrack_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# FILE: sklearntrack_backend/celery.py (Add to existing file)
# ============================================================================

# Add this to your existing celery.py file

from celery.schedules import crontab

app.conf.beat_schedule = {
    # Generate daily reports at 12:01 AM every day
    'generate-daily-reports': {
        'task': 'notes.tasks.generate_daily_reports',
        'schedule': crontab(hour=0, minute=1),
    },
    
    # Clean up old versions every Sunday at 2 AM
    'cleanup-old-versions': {
        'task': 'notes.tasks.cleanup_old_versions',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),
    },
    
    # Auto-tag notes every 6 hours
    'auto-tag-notes': {
        'task': 'notes.tasks.auto_tag_notes',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

app.conf.timezone = 'UTC'
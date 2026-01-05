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
    # Daily backup at 11:50 PM
    'daily-backup-notes': {
        'task': 'notes.tasks.daily_backup_all_notes',
        'schedule': crontab(hour=23, minute=50),
    },
    # Auto-sync updated notes every 30 minutes
    'auto-sync-notes': {
        'task': 'notes.tasks.auto_sync_updated_notes',
        'schedule': crontab(minute='*/30'),
    },
    # Weekly cleanup
    'cleanup-old-versions': {
        'task': 'notes.tasks.cleanup_old_versions',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
    },
}

app.conf.timezone = 'UTC'
# FILE: notes/tasks.py - Fixed imports
# ============================================================================

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
import logging
from django.db import models  # ADD THIS IMPORT

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def auto_sync_updated_notes():
    """
    Auto-sync notes that were updated 1+ hours after last sync
    Runs every 30 minutes
    """
    from .models import Note
    from .google_drive_service import GoogleDriveService  # FIXED IMPORT
    from .pdf_service import export_note_to_pdf  # FIXED IMPORT
    
    # Find notes that need syncing
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    notes_to_sync = Note.objects.filter(
        drive_file_id__isnull=False,  # Only notes already on Drive
        last_drive_sync_at__isnull=False,
        updated_at__gte=one_hour_ago  # Updated in last hour
    ).select_related('user')
    
    synced_count = 0
    error_count = 0
    
    for note in notes_to_sync:
        if note.needs_drive_sync():
            try:
                drive_service = GoogleDriveService(note.user)
                pdf_file = export_note_to_pdf(note)
                filename = f"{note.title}_{timezone.now().date()}.pdf"
                
                result = drive_service.upload_or_update_pdf(
                    pdf_file,
                    filename,
                    existing_file_id=note.drive_file_id
                )
                
                if result['success']:
                    note.last_drive_sync_at = timezone.now()
                    note.upload_type = 'auto'
                    note.save()
                    synced_count += 1
                    logger.info(f"Auto-synced note {note.id} for user {note.user.id}")
                else:
                    error_count += 1
                    logger.error(f"Failed to sync note {note.id}: {result.get('error')}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error syncing note {note.id}: {e}")
    
    return f"Auto-synced {synced_count} notes, {error_count} errors"


@shared_task
def daily_backup_all_notes():
    """
    Daily backup at 11:50 PM
    Upload all notes created/updated today
    """
    from .models import Note
    from .google_drive_service import GoogleDriveService  # FIXED IMPORT
    from .pdf_service import export_note_to_pdf  # FIXED IMPORT
    
    today = timezone.now().date()
    
    # Get all notes created or updated today
    notes_today = Note.objects.filter(
        models.Q(created_at__date=today) | models.Q(updated_at__date=today),
        status='published'
    ).select_related('user').distinct()
    
    uploaded_count = 0
    error_count = 0
    
    for note in notes_today:
        try:
            drive_service = GoogleDriveService(note.user)
            pdf_file = export_note_to_pdf(note)
            filename = f"{note.title}_{today}.pdf"
            
            result = drive_service.upload_or_update_pdf(
                pdf_file,
                filename,
                existing_file_id=note.drive_file_id
            )
            
            if result['success']:
                note.drive_file_id = result['id']
                note.last_drive_sync_at = timezone.now()
                note.upload_type = 'auto'
                note.save()
                uploaded_count += 1
                logger.info(f"Daily backup: note {note.id}")
            else:
                error_count += 1
                logger.error(f"Daily backup failed for note {note.id}: {result.get('error')}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"Daily backup error for note {note.id}: {e}")
    
    return f"Daily backup: {uploaded_count} uploaded, {error_count} errors"


@shared_task
def cleanup_old_versions():
    """Clean up old note versions (keep last 10 per note)"""
    from .models import Note, NoteVersion
    
    notes = Note.objects.all()
    deleted_count = 0
    
    for note in notes:
        versions = note.versions.order_by('-version_number')
        
        if versions.count() > 10:
            old_versions = versions[10:]
            count = old_versions.count()
            old_versions.delete()
            deleted_count += count
    
    return f"Deleted {deleted_count} old versions"
# FILE: notes/tasks.py
# ============================================================================

from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import Note, DailyNoteReport, NoteVersion
from .utils import generate_daily_report_pdf, generate_ai_summary

User = get_user_model()


@shared_task
def auto_save_note_version(note_id):
    """
    Auto-save a note version in the background
    
    Args:
        note_id: ID of the note to version
    """
    try:
        note = Note.objects.get(id=note_id)
        
        # Check if we need to create a new version
        # Only create if there have been significant changes
        last_version = note.versions.order_by('-version_number').first()
        
        if not last_version or (timezone.now() - last_version.saved_at).seconds > 300:
            version_number = note.versions.count() + 1
            NoteVersion.objects.create(
                note=note,
                version_number=version_number,
                content=note.content,
                content_json=note.content_json,
                changes_summary=f"Auto-save at {timezone.now()}"
            )
            return f"Version {version_number} created for note {note_id}"
        
        return "No version created - too recent"
    except Note.DoesNotExist:
        return f"Note {note_id} not found"


@shared_task
def generate_daily_reports():
    """
    Generate daily learning reports for all active users
    Runs at 12:01 AM every day via Celery Beat
    """
    yesterday = date.today() - timedelta(days=1)
    users = User.objects.filter(is_active=True)
    
    reports_generated = 0
    
    for user in users:
        # Get yesterday's activity
        notes_created = Note.objects.filter(
            user=user,
            created_at__date=yesterday
        ).count()
        
        notes_updated = Note.objects.filter(
            user=user,
            updated_at__date=yesterday
        ).exclude(created_at__date=yesterday).count()
        
        # Skip if no activity
        if notes_created == 0 and notes_updated == 0:
            continue
        
        # Get topics covered
        topics = Note.objects.filter(
            user=user,
            session_date=yesterday
        ).values_list('topic__title', flat=True).distinct()
        
        topics_list = [t for t in topics if t]
        
        # Calculate time spent (approximate based on notes)
        time_spent = (notes_created * 30) + (notes_updated * 15)  # Rough estimate
        
        # Get all notes content for AI summary
        daily_notes = Note.objects.filter(
            user=user,
            session_date=yesterday
        )
        
        combined_content = "\n\n".join([note.content[:500] for note in daily_notes])
        
        # Generate AI summary
        ai_summary = generate_ai_summary(
            f"Summarize the following learning activities:\n{combined_content}",
            length='medium'
        )
        
        # Create or update report
        report, created = DailyNoteReport.objects.update_or_create(
            user=user,
            report_date=yesterday,
            defaults={
                'notes_created': notes_created,
                'notes_updated': notes_updated,
                'topics_covered': topics_list,
                'time_spent_minutes': time_spent,
                'ai_summary': ai_summary
            }
        )
        
        # Generate PDF
        try:
            pdf_file = generate_daily_report_pdf(report)
            report.pdf_file = pdf_file
            report.save()
        except Exception as e:
            print(f"Error generating PDF for user {user.id}: {e}")
        
        # Send email
        send_daily_report_email.delay(report.id)
        
        reports_generated += 1
    
    return f"Generated {reports_generated} daily reports"


@shared_task
def send_daily_report_email(report_id):
    """
    Send daily report via email
    
    Args:
        report_id: ID of the DailyNoteReport
    """
    try:
        report = DailyNoteReport.objects.get(id=report_id)
        user = report.user
        
        # Email subject
        subject = f"Daily Learning Report - {report.report_date.strftime('%B %d, %Y')}"
        
        # Email body
        body = f"""
Dear {user.full_name},

Here is your daily learning summary for {report.report_date.strftime('%B %d, %Y')}:

📝 Notes Created: {report.notes_created}
✏️ Notes Updated: {report.notes_updated}
⏱️ Time Spent: {report.time_spent_minutes} minutes

Topics Covered:
{chr(10).join([f"• {topic}" for topic in report.topics_covered])}

Summary:
{report.ai_summary}

Your detailed PDF report is attached.

Keep up the great learning!

Best regards,
SK-LearnTrack Team
        """
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email='noreply@sklearntrack.com',
            to=[user.email]
        )
        
        # Attach PDF if available
        if report.pdf_file:
            email.attach_file(report.pdf_file.path)
        
        # Send email
        email.send()
        
        # Update report
        report.email_sent = True
        report.email_sent_at = timezone.now()
        report.save()
        
        return f"Email sent to {user.email}"
    
    except DailyNoteReport.DoesNotExist:
        return f"Report {report_id} not found"
    except Exception as e:
        return f"Error sending email: {e}"


@shared_task
def cleanup_old_versions():
    """
    Clean up old note versions (keep last 10 per note)
    Runs weekly via Celery Beat
    """
    notes = Note.objects.all()
    deleted_count = 0
    
    for note in notes:
        versions = note.versions.order_by('-version_number')
        
        # Keep only the last 10 versions
        if versions.count() > 10:
            old_versions = versions[10:]
            count = old_versions.count()
            old_versions.delete()
            deleted_count += count
    
    return f"Deleted {deleted_count} old versions"


@shared_task
def generate_ai_note_from_source(source_id, note_title=None):
    """
    Generate notes from a source using AI
    
    Args:
        source_id: ID of the NoteSource
        note_title: Optional title for the note
    """
    from .models import NoteSource, AIGeneratedNote
    
    try:
        source = NoteSource.objects.get(id=source_id)
        
        # Fetch content based on source type
        if source.source_type == 'youtube':
            from .utils import fetch_youtube_transcript, generate_notes_from_transcript
            video_data = fetch_youtube_transcript(source.url)
            content = video_data['transcript']
            generated_notes = generate_notes_from_transcript(content)
        else:
            # For URLs, PDFs, etc. - would need different handlers
            generated_notes = f"Notes generated from: {source.title}"
        
        # Create note
        note = Note.objects.create(
            user=source.user,
            title=note_title or f"Notes: {source.title}",
            content=generated_notes,
            status='draft'
        )
        note.sources.add(source)
        
        # Track AI generation
        AIGeneratedNote.objects.create(
            user=source.user,
            note=note,
            action_type='from_transcript' if source.source_type == 'youtube' else 'from_text',
            source_content=source.url,
            generated_content=generated_notes
        )
        
        return f"Note {note.id} generated from source {source_id}"
    
    except NoteSource.DoesNotExist:
        return f"Source {source_id} not found"


@shared_task
def batch_export_notes(user_id, export_type='full', **kwargs):
    """
    Batch export notes to PDF
    
    Args:
        user_id: User ID
        export_type: 'daily', 'full', or 'topic'
        kwargs: Additional parameters (date, topic_id, etc.)
    """
    from .utils import export_note_to_pdf
    import zipfile
    from io import BytesIO
    
    try:
        user = User.objects.get(id=user_id)
        notes = Note.objects.filter(user=user)
        
        if export_type == 'daily':
            target_date = kwargs.get('date', date.today())
            notes = notes.filter(session_date=target_date)
        elif export_type == 'topic':
            topic_id = kwargs.get('topic_id')
            notes = notes.filter(topic_id=topic_id)
        
        # Create zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for note in notes:
                pdf_file = export_note_to_pdf(note)
                if pdf_file:
                    zip_file.writestr(
                        f"{note.slug}.pdf",
                        pdf_file.read()
                    )
        
        # TODO: Save zip file and send download link to user
        
        return f"Exported {notes.count()} notes for user {user_id}"
    
    except User.DoesNotExist:
        return f"User {user_id} not found"


@shared_task
def auto_tag_notes():
    """
    Automatically suggest tags for notes using AI
    Runs periodically for notes without tags
    """
    # Get notes without tags
    notes = Note.objects.filter(tags=[])[:50]  # Process 50 at a time
    
    processed = 0
    for note in notes:
        # TODO: Use AI to generate tags based on content
        # For now, extract common keywords
        content_lower = note.content.lower()
        
        # Simple keyword extraction (replace with proper NLP)
        common_topics = ['python', 'javascript', 'react', 'django', 'machine learning', 'data science']
        suggested_tags = [topic for topic in common_topics if topic in content_lower]
        
        if suggested_tags:
            note.tags = suggested_tags[:5]  # Limit to 5 tags
            note.save()
            processed += 1
    
    return f"Auto-tagged {processed} notes"
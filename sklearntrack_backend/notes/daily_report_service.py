# FILE: daily_report_service.py
# ============================================================================

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging
from .models import Note, ChapterTopic

logger = logging.getLogger(__name__)


class DailyNotesReportService:
    """Service for generating and sending daily learning reports"""
    
    @staticmethod
    def generate_daily_report(user):
        """Generate daily report data for a user"""
        today = timezone.now().date()
        
        # Notes created today
        notes_created = Note.objects.filter(
            user=user,
            created_at__date=today
        ).count()
        
        # Notes updated today
        notes_updated = Note.objects.filter(
            user=user,
            updated_at__date=today
        ).exclude(created_at__date=today).count()
        
        # Topics created today
        topics_created = ChapterTopic.objects.filter(
            chapter__note__user=user,
            created_at__date=today
        ).count()
        
        # Estimate study time (5 minutes per topic)
        study_time_estimate = topics_created * 5
        
        # Notes list
        notes_list = Note.objects.filter(
            user=user,
            updated_at__date=today
        ).distinct()
        
        return {
            'date': today.strftime('%B %d, %Y'),
            'notes_created': notes_created,
            'notes_updated': notes_updated,
            'topics_created': topics_created,
            'study_time_estimate': study_time_estimate,
            'notes_list': notes_list
        }
    
    @staticmethod
    def send_daily_report_email(user, report_data):
        """Send daily report via email"""
        try:
            # Create notes list HTML
            notes_html = ""
            if report_data['notes_list']:
                notes_items = ''.join([
                    f'<li><strong>{note.title}</strong> ({note.chapters.count()} chapters, {note.status})</li>' 
                    for note in report_data['notes_list']
                ])
                notes_html = f"""
                <h3>📝 Notes Worked On Today</h3>
                <ul>
                    {notes_items}
                </ul>
                """
            
            # Create HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
                    .stat-box {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .stat-number {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📚 Daily Learning Report</h1>
                    <p>{report_data['date']}</p>
                </div>
                <div class="content">
                    <h2>Hello {user.first_name or user.username}!</h2>
                    <p>Here's your learning activity summary for today:</p>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div>Notes Created</div>
                            <div class="stat-number" style="color: #667eea;">{report_data['notes_created']}</div>
                        </div>
                        <div class="stat-box">
                            <div>Notes Updated</div>
                            <div class="stat-number" style="color: #10b981;">{report_data['notes_updated']}</div>
                        </div>
                        <div class="stat-box">
                            <div>Topics Added</div>
                            <div class="stat-number" style="color: #8b5cf6;">{report_data['topics_created']}</div>
                        </div>
                        <div class="stat-box">
                            <div>Study Time</div>
                            <div class="stat-number" style="color: #f59e0b;">{report_data['study_time_estimate']} min</div>
                        </div>
                    </div>
                    
                    {notes_html}
                    
                    <p>Keep up the great work! Your consistency is key to mastering new concepts.</p>
                    
                    <div class="footer">
                        <p>This is an automated report from SK-LearnTrack.</p>
                        <p>You can adjust email preferences in your account settings.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            text_content = f"""
            Daily Learning Report - {report_data['date']}
            
            Hello {user.first_name or user.username}!
            
            Here's your learning activity summary for today:
            
            • Notes Created: {report_data['notes_created']}
            • Notes Updated: {report_data['notes_updated']}
            • Topics Added: {report_data['topics_created']}
            • Estimated Study Time: {report_data['study_time_estimate']} minutes
            """
            
            # Add notes list to text content
            if report_data['notes_list']:
                text_content += "\n\nNotes worked on today:\n"
                for note in report_data['notes_list']:
                    text_content += f"  - {note.title} ({note.chapters.count()} chapters, {note.status})\n"
            
            text_content += """
            
            Keep up the great work! Your consistency is key to mastering new concepts.
            
            ---
            This is an automated report from SK-LearnTrack.
            You can adjust email preferences in your account settings.
            """
            
            # Send email
            email = EmailMultiAlternatives(
                subject=f'📚 Your Daily Learning Report - {report_data["date"]}',
                body=text_content,  # plain text
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Test if email settings work
            logger.info(f"Attempting to send daily report email to {user.email}")
            
            email.send(fail_silently=False)
            
            logger.info(f"Daily report email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"Email sending error: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            print(error_msg)  # Also print to console for immediate visibility
            return False
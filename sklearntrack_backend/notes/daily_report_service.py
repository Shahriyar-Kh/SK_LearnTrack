# FILE: daily_report_service.py - FIXED SENDGRID INTEGRATION
# ============================================================================

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives, get_connection
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
    def _create_email_content(user, report_data):
        """Create HTML and text content optimized to avoid spam"""
        
        # Create simple notes list
        notes_list_text = ""
        if report_data['notes_list']:
            notes_list_text = "\n\nYou worked on these notes today:\n"
            for note in report_data['notes_list']:
                notes_list_text += f"- {note.title} ({note.chapters.count()} chapters, {note.status})\n"
        
        # MINIMAL HTML - looks like a receipt/notification
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #333; margin-bottom: 5px;">SK LearnTrack</h2>
                <p style="color: #666; margin: 0;">Daily Learning Activity Report</p>
                <p style="color: #999; font-size: 14px;">{report_data['date']}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <p style="margin: 0 0 10px;">Hello <strong>{user.first_name or user.username}</strong>,</p>
                <p style="margin: 0;">Here's a summary of your learning activity:</p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 20px 0;">
                <div style="text-align: center; padding: 15px; background: white; border: 1px solid #ddd; border-radius: 6px;">
                    <div style="font-size: 24px; font-weight: bold; color: #007bff;">{report_data['notes_created']}</div>
                    <div style="font-size: 12px; color: #666;">Notes Created</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border: 1px solid #ddd; border-radius: 6px;">
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">{report_data['notes_updated']}</div>
                    <div style="font-size: 12px; color: #666;">Notes Updated</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border: 1px solid #ddd; border-radius: 6px;">
                    <div style="font-size: 24px; font-weight: bold; color: #6f42c1;">{report_data['topics_created']}</div>
                    <div style="font-size: 12px; color: #666;">Topics Added</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border: 1px solid #ddd; border-radius: 6px;">
                    <div style="font-size: 24px; font-weight: bold; color: #fd7e14;">{report_data['study_time_estimate']} min</div>
                    <div style="font-size: 12px; color: #666;">Study Time</div>
                </div>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; text-align: center;">
                <p style="margin: 0 0 10px;">
                    This is an automated learning activity report.<br>
                    Manage your email preferences in your account settings.
                </p>
                <p style="margin: 0; font-size: 11px;">
                    <a href="https://sk-learntrack.vercel.app/settings" style="color: #007bff; text-decoration: none;">Settings</a> | 
                    <a href="https://sk-learntrack.vercel.app/unsubscribe" style="color: #666; text-decoration: none;">Unsubscribe</a>
                </p>
            </div>
        </div>
        """
        
        # PLAIN TEXT VERSION (very important for spam filters)
        text_content = f"""SK LearnTrack - Daily Learning Activity Report
    {report_data['date']}

    Hello {user.first_name or user.username},

    Here's a summary of your learning activity today:

    • Notes Created: {report_data['notes_created']}
    • Notes Updated: {report_data['notes_updated']}
    • Topics Added: {report_data['topics_created']}
    • Study Time: {report_data['study_time_estimate']} minutes
    {notes_list_text}

    This is an automated learning activity report.

    Manage your email preferences: https://sk-learntrack.vercel.app/settings
    Unsubscribe: https://sk-learntrack.vercel.app/unsubscribe

    ---
    SK LearnTrack
    """
        
        return html_content, text_content
    
    @staticmethod
    def send_daily_report_email(user, report_data):
        """Send daily report via email with SendGrid API priority"""
        try:
            # Validate user has email
            if not user.email:
                logger.error(f"User {user.username} has no email address configured")
                return False
            
            logger.info(f"Attempting to send daily report email to {user.email}")
            
            # Check if SendGrid API key is available
            sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
            
            if sendgrid_api_key and sendgrid_api_key.strip():
                logger.info("Using SendGrid API for email delivery")
                return DailyNotesReportService._send_via_sendgrid_api(user, report_data, sendgrid_api_key)
            else:
                logger.warning("SendGrid API key not configured, falling back to SMTP")
                return DailyNotesReportService._send_via_smtp(user, report_data)
            
        except Exception as e:
            import traceback
            error_msg = f"Email sending error for user {user.username}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            print(f"[EMAIL ERROR] {error_msg}")
            return False
    
    @staticmethod
    def _send_via_sendgrid_api(user, report_data, api_key):
        """Send email using SendGrid API directly"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            # Create email content
            html_content, text_content = DailyNotesReportService._create_email_content(user, report_data)
            
            # Initialize SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            
            # Create mail object
            from_email = Email(settings.DEFAULT_FROM_EMAIL)
            to_email = To(user.email)
            subject = f'📚 Your Daily Learning Report - {report_data["date"]}'
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=Content("text/plain", text_content),
                html_content=Content("text/html", html_content)
            )
            
            # Send email with timeout
            import socket
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(10)  # 10 second timeout
            
            try:
                response = sg.send(mail)
                logger.info(f"✅ SendGrid API response: {response.status_code}")
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"✅ Email sent successfully via SendGrid API to {user.email}")
                    return True
                else:
                    logger.error(f"❌ SendGrid API error: {response.status_code} - {response.body}")
                    return False
            finally:
                socket.setdefaulttimeout(original_timeout)
            
        except ImportError:
            logger.error("SendGrid library not installed. Run: pip install sendgrid")
            return False
        except Exception as e:
            logger.error(f"SendGrid API error: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_smtp(user, report_data):
        """Fallback to SMTP if SendGrid API is not available"""
        try:
            # Validate SMTP settings
            required_settings = ['EMAIL_HOST', 'EMAIL_PORT', 'DEFAULT_FROM_EMAIL']
            for setting in required_settings:
                if not hasattr(settings, setting) or not getattr(settings, setting):
                    logger.error(f"SMTP configuration missing: {setting}")
                    return False
            
            # Create email content
            html_content, text_content = DailyNotesReportService._create_email_content(user, report_data)
            
            # Test SMTP connection with shorter timeout
            try:
                connection = get_connection(timeout=5)
                connection.open()
                logger.info(f"SMTP connection successful: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                connection.close()
            except Exception as conn_error:
                logger.error(f"SMTP connection failed: {str(conn_error)}")
                return False
            
            # Create and send email via SMTP with timeout
            email = EmailMultiAlternatives(
                subject=f'📚 Your Daily Learning Report - {report_data["date"]}',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
                reply_to=[settings.DEFAULT_FROM_EMAIL],
                connection=get_connection(timeout=10)
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send with timeout
            email.send(fail_silently=False)
            
            logger.info(f"Daily report email sent successfully via SMTP to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP sending error: {str(e)}")
            return False
    
    @staticmethod
    def check_email_configuration():
        """Check email configuration status"""
        config_status = {
            'sendgrid_available': bool(
                hasattr(settings, 'SENDGRID_API_KEY') and 
                settings.SENDGRID_API_KEY and 
                settings.SENDGRID_API_KEY.strip()
            ),
            'smtp_available': bool(
                hasattr(settings, 'EMAIL_HOST') and 
                hasattr(settings, 'EMAIL_PORT') and
                hasattr(settings, 'DEFAULT_FROM_EMAIL')
            ),
            'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET'),
            'email_backend': getattr(settings, 'EMAIL_BACKEND', 'NOT SET'),
        }
        
        logger.info(f"Email Configuration: {config_status}")
        
        return config_status
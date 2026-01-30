# FILE: daily_report_service.py - IMPROVED WITH UNIFIED EMAIL SERVICE
# ============================================================================

from django.utils import timezone
from django.conf import settings
import logging
from .models import Note, ChapterTopic

logger = logging.getLogger(__name__)

# Import the unified email service
try:
    from .email_service import EmailService
except ImportError:
    logger.warning("EmailService not found, will use fallback method")
    EmailService = None


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
        
        # Notes updated today (excluding newly created ones)
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
        
        # Get notes list worked on today
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
        """
        Create HTML and text content for the email
        Optimized to avoid spam filters
        """
        
        # Create notes list text
        notes_list_text = ""
        if report_data['notes_list']:
            notes_list_text = "\n\nYou worked on these notes today:\n"
            for note in report_data['notes_list']:
                notes_list_text += f"- {note.title} ({note.chapters.count()} chapters, {note.status})\n"
        
        # HTML content - clean and professional
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">SK LearnTrack</h1>
                    <p style="color: #ffffff; margin: 10px 0 0 0; opacity: 0.9;">Daily Learning Activity Report</p>
                    <p style="color: #ffffff; margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">{report_data['date']}</p>
                </div>
                
                <!-- Greeting -->
                <div style="padding: 30px;">
                    <p style="margin: 0 0 20px; font-size: 16px; color: #333333;">
                        Hello <strong>{user.first_name or user.username}</strong>,
                    </p>
                    <p style="margin: 0 0 30px; font-size: 14px; color: #666666; line-height: 1.6;">
                        Here's a summary of your learning activity today. Keep up the great work!
                    </p>
                    
                    <!-- Stats Grid -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                        <tr>
                            <td width="48%" style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center;">
                                <div style="font-size: 32px; font-weight: bold; color: #667eea; margin-bottom: 5px;">
                                    {report_data['notes_created']}
                                </div>
                                <div style="font-size: 12px; color: #666666; text-transform: uppercase; letter-spacing: 1px;">
                                    Notes Created
                                </div>
                            </td>
                            <td width="4%"></td>
                            <td width="48%" style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center;">
                                <div style="font-size: 32px; font-weight: bold; color: #10b981; margin-bottom: 5px;">
                                    {report_data['notes_updated']}
                                </div>
                                <div style="font-size: 12px; color: #666666; text-transform: uppercase; letter-spacing: 1px;">
                                    Notes Updated
                                </div>
                            </td>
                        </tr>
                        <tr><td colspan="3" height="10"></td></tr>
                        <tr>
                            <td width="48%" style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center;">
                                <div style="font-size: 32px; font-weight: bold; color: #8b5cf6; margin-bottom: 5px;">
                                    {report_data['topics_created']}
                                </div>
                                <div style="font-size: 12px; color: #666666; text-transform: uppercase; letter-spacing: 1px;">
                                    Topics Added
                                </div>
                            </td>
                            <td width="4%"></td>
                            <td width="48%" style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center;">
                                <div style="font-size: 32px; font-weight: bold; color: #f59e0b; margin-bottom: 5px;">
                                    {report_data['study_time_estimate']}
                                </div>
                                <div style="font-size: 12px; color: #666666; text-transform: uppercase; letter-spacing: 1px;">
                                    Study Minutes
                                </div>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Encouragement -->
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin-bottom: 30px; border-radius: 4px;">
                        <p style="margin: 0; font-size: 14px; color: #92400e;">
                            💡 <strong>Keep Going!</strong> Consistency is the key to mastering new concepts.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0 0 10px; font-size: 12px; color: #666666;">
                        This is an automated learning activity report from SK LearnTrack.
                    </p>
                    <p style="margin: 0; font-size: 11px; color: #999999;">
                        <a href="https://sk-learntrack.vercel.app/settings" style="color: #667eea; text-decoration: none;">Email Preferences</a>
                        | 
                        <a href="https://sk-learntrack.vercel.app" style="color: #999999; text-decoration: none;">Visit Dashboard</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version (critical for deliverability)
        text_content = f"""
SK LearnTrack - Daily Learning Activity Report
{report_data['date']}

Hello {user.first_name or user.username},

Here's a summary of your learning activity today:

STATISTICS:
• Notes Created: {report_data['notes_created']}
• Notes Updated: {report_data['notes_updated']}
• Topics Added: {report_data['topics_created']}
• Study Time: {report_data['study_time_estimate']} minutes
{notes_list_text}

Keep up the great work! Consistency is the key to mastering new concepts.

---
This is an automated learning activity report.

Manage your preferences: https://sk-learntrack.vercel.app/settings
Visit your dashboard: https://sk-learntrack.vercel.app

SK LearnTrack Team
        """.strip()
        
        return html_content, text_content
    
    @staticmethod
    def send_daily_report_email(user, report_data):
        """
        Send daily report via email using the unified EmailService
        
        Args:
            user: User object
            report_data: Report data dictionary
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Validate user has email
            if not user.email:
                logger.error(f"❌ User {user.username} has no email address")
                return False
            
            logger.info(f"📧 Sending daily report to: {user.email}")
            
            # Create email content
            html_content, text_content = DailyNotesReportService._create_email_content(
                user, report_data
            )
            
            # Create subject
            subject = f'📚 Your Daily Learning Report - {report_data["date"]}'
            
            # Check if EmailService is available
            if EmailService:
                # Use unified email service (recommended)
                success = EmailService.send_email(
                    to_email=user.email,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL
                )
                
                if success:
                    logger.info(f"✅ Daily report email sent to {user.email}")
                else:
                    logger.error(f"❌ Failed to send daily report to {user.email}")
                
                return success
            else:
                # Fallback to direct Django mail
                logger.warning("Using fallback email method")
                return DailyNotesReportService._send_fallback(
                    user, subject, text_content, html_content
                )
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Daily report email error: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def _send_fallback(user, subject, text_content, html_content):
        """Fallback email sending using Django's EmailMultiAlternatives"""
        try:
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            
            if html_content:
                email.attach_alternative(html_content, "text/html")
            
            email.send(fail_silently=False)
            logger.info(f"✅ Email sent via fallback method to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fallback email sending failed: {str(e)}")
            return False
    
    @staticmethod
    def check_email_configuration():
        """
        Check email configuration status
        
        Returns:
            dict: Configuration status
        """
        if EmailService:
            return EmailService.test_email_configuration()
        else:
            return {
                'status': 'EmailService not available',
                'email_backend': settings.EMAIL_BACKEND,
                'default_from_email': settings.DEFAULT_FROM_EMAIL
            }
# FILE: sendgrid_service.py
# ============================================================================

import sendgrid
from sendgrid.helpers.mail import Mail, Content, To
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SendGridEmailService:
    """SendGrid specific email service"""
    
    @staticmethod
    def send_daily_report(user, report_data):
        """Send daily report via SendGrid"""
        try:
            # Initialize SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            
            # Prepare email content
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
                    
                    <p>Keep up the great work! Your consistency is key to mastering new concepts.</p>
                    
                    <div class="footer">
                        <p>This is an automated report from SK-LearnTrack.</p>
                        <p>You can adjust email preferences in your account settings.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendGrid mail object
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email
            subject = f'📚 Your Daily Learning Report - {report_data["date"]}'
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Send email
            response = sg.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ SendGrid email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"❌ SendGrid error: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid email error: {str(e)}")
            return False
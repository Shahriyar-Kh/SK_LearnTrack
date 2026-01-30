# FILE: notes/email_service.py - IMPROVED WITH 403 HANDLING
# ============================================================================
# This version handles SendGrid 403 errors gracefully and works better in dev
# ============================================================================

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Unified email service that handles both SendGrid and SMTP
    with proper error handling for development and production.
    """
    
    @staticmethod
    def send_email(
        to_email,
        subject,
        text_content,
        html_content=None,
        from_email=None,
        reply_to=None
    ):
        """
        Send email using best available method
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Validate inputs
            if not to_email or not subject or not text_content:
                logger.error("❌ Email sending failed: Missing required fields")
                return False
            
            # Use default from_email if not provided
            if not from_email:
                from_email = settings.DEFAULT_FROM_EMAIL
            
            logger.info(f"📧 Attempting to send email to: {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   From: {from_email}")
            
            # Check if we're in development mode
            if settings.DEBUG:
                logger.info("   Method: Console (Development Mode)")
                return EmailService._send_via_console(
                    to_email=to_email,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content,
                    from_email=from_email
                )
            
            # Production mode - try SendGrid first
            sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', '').strip()
            
            if sendgrid_api_key and len(sendgrid_api_key) > 20:
                logger.info("   Method: SendGrid API")
                success = EmailService._send_via_sendgrid_api(
                    to_email=to_email,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content,
                    from_email=from_email,
                    api_key=sendgrid_api_key
                )
                
                # If SendGrid fails with 403, fall back to console in development
                if not success and settings.DEBUG:
                    logger.warning("⚠️  SendGrid failed, falling back to console")
                    return EmailService._send_via_console(
                        to_email=to_email,
                        subject=subject,
                        text_content=text_content,
                        html_content=html_content,
                        from_email=from_email
                    )
                
                return success
            else:
                logger.info("   Method: SMTP")
                return EmailService._send_via_smtp(
                    to_email=to_email,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content,
                    from_email=from_email,
                    reply_to=reply_to
                )
                
        except Exception as e:
            logger.error(f"❌ Email sending failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def _send_via_console(to_email, subject, text_content, html_content, from_email):
        """
        Send email to console (development mode)
        """
        try:
            from django.core.mail import send_mail
            
            # This will print to console
            send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False
            )
            
            logger.info(f"✅ Email printed to console")
            logger.info("=" * 60)
            logger.info(f"TO: {to_email}")
            logger.info(f"FROM: {from_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info("-" * 60)
            logger.info(text_content[:500])
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"❌ Console email failed: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_sendgrid_api(to_email, subject, text_content, html_content, from_email, api_key):
        """
        Send email using SendGrid API
        """
        try:
            # Import SendGrid
            try:
                import sendgrid
                from sendgrid.helpers.mail import Mail, Email, To, Content
            except ImportError:
                logger.error("❌ SendGrid library not installed")
                logger.error("   Install with: pip install sendgrid")
                return False
            
            # Validate API key format
            if not api_key.startswith('SG.'):
                logger.warning("⚠️  SendGrid API key format unusual (should start with 'SG.')")
            
            # Create SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            
            # Create mail object
            message = Mail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_content),
                html_content=Content("text/html", html_content) if html_content else None
            )
            
            # Send with timeout protection
            import socket
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(20)
            
            try:
                response = sg.send(message)
                
                logger.info(f"   SendGrid Status: {response.status_code}")
                
                if response.status_code == 202:
                    logger.info(f"✅ Email accepted by SendGrid for delivery to {to_email}")
                    return True
                    
                elif response.status_code == 401:
                    logger.error("❌ SendGrid 401: Invalid API key")
                    logger.error("   Check your SENDGRID_API_KEY environment variable")
                    return False
                    
                elif response.status_code == 403:
                    # Parse error details
                    try:
                        error_body = response.body.decode('utf-8') if response.body else "No details"
                        logger.error(f"❌ SendGrid 403 Forbidden: {error_body}")
                        
                        logger.error("")
                        logger.error("🔧 HOW TO FIX SendGrid 403 Error:")
                        logger.error("")
                        logger.error("   Your sender email is NOT VERIFIED in SendGrid!")
                        logger.error("")
                        logger.error("   Step 1: Go to SendGrid Dashboard")
                        logger.error("   https://app.sendgrid.com/settings/sender_auth")
                        logger.error("")
                        logger.error("   Step 2: Click 'Verify a Single Sender'")
                        logger.error("")
                        logger.error(f"   Step 3: Add and verify: {from_email}")
                        logger.error("")
                        logger.error("   Step 4: Check your email and click verification link")
                        logger.error("")
                        logger.error("   Step 5: Wait 5-10 minutes for verification to activate")
                        logger.error("")
                        logger.error("   OR for development: Disable SendGrid in settings.py")
                        logger.error("")
                        
                    except:
                        logger.error("   Unable to parse error details")
                    
                    return False
                    
                elif response.status_code == 429:
                    logger.error("❌ SendGrid 429: Rate limit exceeded")
                    return False
                    
                else:
                    error_body = response.body.decode('utf-8') if response.body else "Unknown error"
                    logger.error(f"❌ SendGrid Error {response.status_code}: {error_body}")
                    return False
                    
            finally:
                socket.setdefaulttimeout(original_timeout)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ SendGrid API Exception: {error_msg}")
            
            if "403" in error_msg or "Forbidden" in error_msg:
                logger.error("")
                logger.error("🔧 QUICK FIX FOR DEVELOPMENT:")
                logger.error("   Add to your .env file:")
                logger.error("   SENDGRID_API_KEY=")
                logger.error("")
                logger.error("   Or in settings.py, add:")
                logger.error("   if DEBUG:")
                logger.error("       SENDGRID_API_KEY = ''")
                logger.error("")
            
            return False
    
    @staticmethod
    def _send_via_smtp(to_email, subject, text_content, html_content, from_email, reply_to=None):
        """
        Send email using SMTP
        """
        try:
            # Check SMTP configuration
            if not settings.EMAIL_HOST:
                logger.error("❌ EMAIL_HOST not configured")
                return False
            
            # Test connection
            try:
                connection = get_connection(timeout=5)
                connection.open()
                logger.info(f"✅ SMTP connection successful: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                connection.close()
            except Exception as conn_error:
                logger.error(f"❌ SMTP connection failed: {str(conn_error)}")
                return False
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[to_email],
                reply_to=[reply_to or from_email],
                connection=get_connection(timeout=15)
            )
            
            if html_content:
                email.attach_alternative(html_content, "text/html")
            
            email.send(fail_silently=False)
            
            logger.info(f"✅ Email sent via SMTP to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ SMTP sending failed: {str(e)}")
            return False
    
    @staticmethod
    def test_email_configuration():
        """
        Test email configuration and return status
        """
        status_report = {
            'debug_mode': settings.DEBUG,
            'sendgrid_api_available': False,
            'sendgrid_api_valid': False,
            'smtp_configured': False,
            'email_backend': settings.EMAIL_BACKEND,
            'recommended_method': None,
            'issues': [],
            'from_email': settings.DEFAULT_FROM_EMAIL
        }
        
        # Check SendGrid API
        sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', '').strip()
        if sendgrid_key:
            status_report['sendgrid_api_available'] = True
            
            if sendgrid_key.startswith('SG.') and len(sendgrid_key) > 20:
                status_report['sendgrid_api_valid'] = True
                if not settings.DEBUG:
                    status_report['recommended_method'] = 'SendGrid API'
            else:
                status_report['issues'].append(
                    "SendGrid API key format invalid"
                )
        
        # Check SMTP
        if settings.EMAIL_HOST and settings.EMAIL_PORT:
            status_report['smtp_configured'] = True
            if not status_report['recommended_method']:
                status_report['recommended_method'] = 'SMTP'
        
        # Development mode
        if settings.DEBUG:
            status_report['recommended_method'] = 'Console (Development)'
        
        # Overall recommendation
        if not status_report['recommended_method']:
            status_report['recommended_method'] = 'NONE - Email not configured'
            status_report['issues'].append("No email method available")
        
        # Log status
        logger.info("=" * 60)
        logger.info("📧 EMAIL CONFIGURATION STATUS")
        logger.info(f"   Debug Mode: {status_report['debug_mode']}")
        logger.info(f"   Backend: {status_report['email_backend']}")
        logger.info(f"   From Email: {status_report['from_email']}")
        logger.info(f"   SendGrid API: {'✅ Available' if status_report['sendgrid_api_available'] else '❌ Not Available'}")
        logger.info(f"   SMTP: {'✅ Configured' if status_report['smtp_configured'] else '❌ Not Configured'}")
        logger.info(f"   Recommended: {status_report['recommended_method']}")
        
        if status_report['issues']:
            logger.warning("   Issues:")
            for issue in status_report['issues']:
                logger.warning(f"   - {issue}")
        
        logger.info("=" * 60)
        
        return status_report
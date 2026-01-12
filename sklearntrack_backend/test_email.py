# FILE: manage.py (add after existing imports)
# Or create a new file: test_email.py
import os
import django
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sklearntrack_backend.settings')
django.setup()

def test_sendgrid():
    try:
        send_mail(
            subject='Test Email from SendGrid',
            message='This is a test email from SK-LearnTrack with SendGrid.',
            from_email='noreply@sklearntrack.com',
            recipient_list=['shahriyarkhanpk3@gmail.com'],  # Replace with your email
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

if __name__ == '__main__':
    test_sendgrid()
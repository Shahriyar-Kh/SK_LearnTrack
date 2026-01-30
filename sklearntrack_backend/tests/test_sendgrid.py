#!/usr/bin/env python
"""
Test SendGrid configuration directly
"""
import os
import sys
import logging
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sklearntrack_backend.settings')
import django
django.setup()

logger = logging.getLogger(__name__)

def test_sendgrid_direct():
    """Test SendGrid API directly"""
    api_key = getattr(settings, 'SENDGRID_API_KEY', '')
    
    if not api_key:
        print("❌ SENDGRID_API_KEY not found in settings")
        return False
    
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Length: {len(api_key)} characters")
    
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        sg = sendgrid.SendGridAPIClient(api_key=api_key.strip())
        
        # Test API key by making a simple request
        response = sg.client.api_keys._(api_key).get()
        
        if response.status_code == 200:
            print("✅ SendGrid API key is valid")
            
            # Check permissions
            import json
            data = json.loads(response.body)
            scopes = data.get('scopes', [])
            
            print(f"📋 Permissions: {', '.join(scopes)}")
            
            if 'mail.send' in scopes:
                print("✅ 'mail.send' permission granted")
            else:
                print("❌ MISSING 'mail.send' permission!")
                print("   Go to SendGrid Dashboard → API Keys → Edit")
                print("   Enable 'Mail Send' permission")
                return False
                
            return True
        else:
            print(f"❌ SendGrid API key validation failed: {response.status_code}")
            return False
            
    except ImportError:
        print("❌ sendgrid library not installed")
        print("   Install with: pip install sendgrid")
        return False
    except Exception as e:
        print(f"❌ SendGrid test error: {str(e)}")
        return False

def test_sendgrid_smtp():
    """Test SendGrid SMTP connection"""
    print("\n🔧 Testing SMTP Configuration:")
    print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"   EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"   EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(f"   DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
    
    try:
        from django.core.mail import get_connection
        
        connection = get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=getattr(settings, 'SENDGRID_API_KEY', ''),
            use_tls=True,
            timeout=10
        )
        
        connection.open()
        print("✅ SMTP connection successful")
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 SENGRID CONFIGURATION TEST")
    print("=" * 60)
    
    api_test = test_sendgrid_direct()
    smtp_test = test_sendgrid_smtp()
    
    print("\n" + "=" * 60)
    if api_test and smtp_test:
        print("✅ All tests passed!")
        print("   SendGrid should be working correctly.")
    else:
        print("❌ Tests failed")
        print("\n📋 NEXT STEPS:")
        print("1. Verify SendGrid API key in Render environment")
        print("2. Ensure sender email is verified in SendGrid")
        print("3. Check API key has 'Mail Send' permission")
        print("4. Test with: python test_sendgrid.py")
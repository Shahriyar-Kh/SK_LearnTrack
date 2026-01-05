# FILE: debug_oauth.py
# ============================================================================

import os
import django
import requests
import pickle
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sklearntrack_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

def check_token_file():
    """Check if token file exists"""
    User = get_user_model()
    try:
        user = User.objects.get(email="sharykingpk2@gmail.com")
        token_path = Path('media/google_tokens') / f'token_{user.id}.pickle'
        
        if token_path.exists():
            print(f"✓ Token file exists at: {token_path}")
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)
            print(f"✓ Credentials loaded")
            print(f"  Valid: {creds.valid}")
            print(f"  Expired: {creds.expired}")
            print(f"  Has refresh token: {bool(creds.refresh_token)}")
            return True
        else:
            print(f"✗ Token file not found at: {token_path}")
            return False
    except Exception as e:
        print(f"✗ Error checking token: {e}")
        return False

def test_auth_url():
    """Test getting auth URL"""
    login_url = "http://localhost:8000/api/token/"
    login_data = {"email": "sharykingpk2@gmail.com", "password": "shary786"}
    
    print("1. Getting JWT token...")
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code == 200:
        access_token = login_response.json()['access']
        print(f"✓ Got JWT token: {access_token[:20]}...")
        
        auth_url = "http://localhost:8000/api/notes/google_auth_url/"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("2. Getting Google OAuth URL...")
        auth_response = requests.get(auth_url, headers=headers)
        
        if auth_response.status_code == 200:
            data = auth_response.json()
            if data['success']:
                print(f"✓ Got OAuth URL")
                print(f"  State format: {data['state']}")
                print(f"  User ID in state: {data['state'].split(':')[0]}")
                print(f"  Session key: {data.get('session_key')}")
                print(f"\n3. Open this URL in browser:")
                print(f"\n{data['auth_url']}\n")
                return data['auth_url']
            else:
                print(f"✗ Failed: {data.get('error')}")
        else:
            print(f"✗ Failed to get auth URL: {auth_response.status_code}")
            print(auth_response.text)
    else:
        print(f"✗ Login failed: {login_response.status_code}")
    
    return None

def test_direct_session():
    """Test session directly"""
    from django.contrib.sessions.backends.db import SessionStore
    from django.contrib.sessions.models import Session
    
    User = get_user_model()
    user = User.objects.get(email="sharykingpk2@gmail.com")
    
    print(f"\nChecking sessions for user {user.id}:")
    
    # Check all sessions
    sessions = Session.objects.all()
    print(f"Total sessions in DB: {sessions.count()}")
    
    for session in sessions:
        session_data = session.get_decoded()
        if 'google_auth_user_id' in session_data:
            print(f"  Found session with google_auth_user_id: {session_data['google_auth_user_id']}")
            print(f"  Session key: {session.session_key}")
            print(f"  State in session: {session_data.get('google_auth_state')}")

if __name__ == '__main__':
    print("=" * 70)
    print("Google OAuth Debug Script")
    print("=" * 70)
    
    # Check if user exists
    User = get_user_model()
    try:
        user = User.objects.get(email="sharykingpk2@gmail.com")
        print(f"✓ Found user: {user.email} (ID: {user.id})")
    except User.DoesNotExist:
        print("✗ User not found")
        exit(1)
    
    # Check media directory
    token_dir = Path('media/google_tokens')
    if not token_dir.exists():
        token_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created token directory: {token_dir}")
    
    print(f"\nCurrent token status:")
    check_token_file()
    
    print(f"\n" + "-" * 70)
    print("Testing OAuth flow...")
    test_auth_url()
    
    print(f"\n" + "-" * 70)
    print("Checking sessions...")
    test_direct_session()
    
    print(f"\n" + "-" * 70)
    print("Instructions:")
    print("1. Copy the OAuth URL above and open in browser")
    print("2. Complete the Google OAuth flow")
    print("3. Run this script again to check if token was saved")
    print("   python debug_oauth.py")
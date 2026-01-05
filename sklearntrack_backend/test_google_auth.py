# FILE: test_google_fix.py
# ============================================================================

import os
import django
import pickle
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sklearntrack_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from notes.google_drive_service import GoogleDriveService

def test_connection():
    User = get_user_model()
    
    try:
        # Get test user
        user = User.objects.get(email='sharykingpk2@gmail.com')
        print(f"Testing connection for user: {user.email}")
        
        # Check if token exists
        token_path = Path('media/google_tokens') / f'token_{user.id}.pickle'
        
        if token_path.exists():
            print(f"✓ Token file exists at: {token_path}")
            
            # Try to load credentials
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)
            
            print(f"✓ Credentials loaded")
            print(f"  - Valid: {creds.valid}")
            print(f"  - Expired: {creds.expired}")
            print(f"  - Scopes: {creds.scopes}")
            
            if creds.expired and creds.refresh_token:
                print("  ! Credentials expired but refresh token available")
            elif not creds.valid:
                print("  ! Credentials invalid")
            else:
                print("  ✓ Credentials valid")
                
        else:
            print(f"✗ Token file not found at: {token_path}")
            print("  You need to authenticate via Google OAuth first.")
            print("  Steps:")
            print("  1. Login to your Django app")
            print("  2. Go to /api/notes/google_auth_url/")
            print("  3. Follow the OAuth flow")
            
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def check_media_dir():
    """Check if media directory structure exists"""
    media_dir = Path('media')
    tokens_dir = media_dir / 'google_tokens'
    
    print(f"\nChecking media directory structure:")
    print(f"  Media root exists: {media_dir.exists()}")
    
    if media_dir.exists():
        print(f"  Google tokens dir exists: {tokens_dir.exists()}")
        
        if tokens_dir.exists():
            token_files = list(tokens_dir.glob('*.pickle'))
            print(f"  Found {len(token_files)} token file(s)")
            for tf in token_files:
                print(f"    - {tf.name}")

if __name__ == '__main__':
    print("=" * 60)
    print("Google Drive Connection Test")
    print("=" * 60)
    
    check_media_dir()
    print("\n" + "-" * 60)
    test_connection()
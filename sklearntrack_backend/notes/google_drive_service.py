# FILE: notes/google_drive_service.py - SCOPE FIX
# ============================================================================
# CRITICAL FIX: Include all OAuth scopes that Google adds automatically
# ============================================================================

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
import os
import pickle
import logging
import secrets
from io import BytesIO
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ✅ CRITICAL FIX: Include ALL scopes that Google adds
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.file'
]

FOLDER_NAME = 'SK-LearnTrack Notes'


class GoogleDriveService:
    """Unified Google Drive integration service"""
    
    def __init__(self, user):
        self.user = user
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _get_token_path(self):
        """Get secure token storage path for user"""
        token_dir = os.path.join(settings.MEDIA_ROOT, 'google_tokens')
        os.makedirs(token_dir, exist_ok=True)
        return os.path.join(token_dir, f'token_{self.user.id}.pickle')
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        token_path = self._get_token_path()
        
        # Load existing credentials
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    self.creds = pickle.load(token)
                logger.info(f"✅ Loaded credentials for user {self.user.id}")
            except (pickle.PickleError, EOFError, KeyError) as e:
                logger.error(f"❌ Corrupted token file for user {self.user.id}: {e}")
                self.creds = None
            except Exception as e:
                logger.error(f"❌ Error loading credentials for user {self.user.id}: {e}")
                self.creds = None
        
        # Refresh or validate credentials
        if self.creds:
            if self.creds.expired and self.creds.refresh_token:
                try:
                    logger.info(f"🔄 Refreshing credentials for user {self.user.id}")
                    self.creds.refresh(Request())
                    # Save refreshed credentials
                    with open(token_path, 'wb') as token:
                        pickle.dump(self.creds, token)
                    logger.info(f"✅ Refreshed credentials for user {self.user.id}")
                except Exception as e:
                    logger.error(f"❌ Error refreshing credentials for user {self.user.id}: {e}")
                    self.creds = None
        
        if not self.creds or not self.creds.valid:
            raise Exception("Google Drive authentication required. Please reconnect.")
        
        # Build service
        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info(f"✅ Drive service built for user {self.user.id}")
        except Exception as e:
            logger.error(f"❌ Error building Drive service for user {self.user.id}: {e}")
            raise
    
    def is_connected(self):
        """Check if user has valid Drive connection"""
        token_path = self._get_token_path()
        if not os.path.exists(token_path):
            return False
        
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            return creds and creds.valid
        except Exception as e:
            logger.error(f"❌ Error checking connection for user {self.user.id}: {e}")
            return False
    
    def test_connection(self):
        """Test if the Google Drive connection is working"""
        try:
            # Simple API call to test connection
            self.service.about().get(fields='user').execute()
            logger.info(f"✅ Drive connection test successful for user {self.user.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed for user {self.user.id}: {e}")
            return False
    
    def get_or_create_folder(self):
        """Get or create SK-LearnTrack Notes folder"""
        try:
            # Search for existing folder
            query = f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                logger.info(f"✅ Found existing folder for user {self.user.id}")
                return folders[0]['id']
            
            # Create new folder
            file_metadata = {
                'name': FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"✅ Created folder '{FOLDER_NAME}' for user {self.user.id}")
            return folder['id']
            
        except HttpError as e:
            logger.error(f"❌ Error managing folder for user {self.user.id}: {e}")
            raise Exception(f"Failed to create folder: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error for user {self.user.id}: {e}")
            raise
    
    def upload_or_update_pdf(self, pdf_file, filename, existing_file_id=None):
        """
        Upload new PDF or update existing one
        
        Args:
            pdf_file: BytesIO PDF content
            filename: Name for the file
            existing_file_id: If provided, updates existing file
            
        Returns:
            dict: File metadata
        """
        try:
            # Ensure we're at the start of the file
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            folder_id = self.get_or_create_folder()
            
            media = MediaIoBaseUpload(
                pdf_file,
                mimetype='application/pdf',
                resumable=True
            )
            
            if existing_file_id:
                # UPDATE existing file
                try:
                    file = self.service.files().update(
                        fileId=existing_file_id,
                        media_body=media,
                        fields='id, webViewLink, webContentLink, modifiedTime'
                    ).execute()
                    
                    logger.info(f"✅ Updated file {existing_file_id} for user {self.user.id}")
                    
                    return {
                        'id': file['id'],
                        'webViewLink': file.get('webViewLink'),
                        'webContentLink': file.get('webContentLink'),
                        'modifiedTime': file.get('modifiedTime'),
                        'success': True,
                        'updated': True
                    }
                except HttpError as e:
                    if e.resp.status == 404:
                        logger.warning(f"⚠️ File {existing_file_id} not found, creating new for user {self.user.id}")
                        existing_file_id = None
                    else:
                        raise
            
            # CREATE new file
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': 'application/pdf'
            }
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink, createdTime'
            ).execute()
            
            # Set file permissions to accessible by link
            self.service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            logger.info(f"✅ Created new file for user {self.user.id}")
            
            return {
                'id': file['id'],
                'webViewLink': file.get('webViewLink'),
                'webContentLink': file.get('webContentLink'),
                'createdTime': file.get('createdTime'),
                'success': True,
                'updated': False
            }
            
        except HttpError as e:
            error_msg = f"HTTP Error uploading to Drive: {e}"
            logger.error(f"❌ {error_msg} for user {self.user.id}")
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Error uploading to Drive: {str(e)}"
            logger.error(f"❌ {error_msg} for user {self.user.id}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def delete_file(self, file_id):
        """Delete a file from Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"✅ Deleted file {file_id} for user {self.user.id}")
            return True
        except HttpError as e:
            logger.error(f"❌ Error deleting file for user {self.user.id}: {e}")
            return False
    
    def list_user_files(self):
        """List all PDF files in the user's folder"""
        try:
            folder_id = self.get_or_create_folder()
            query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, createdTime, modifiedTime, size, webViewLink)',
                orderBy='modifiedTime desc'
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            logger.error(f"❌ Error listing files for user {self.user.id}: {e}")
            return []
    
    def get_file_info(self, file_id):
        """Get detailed information about a specific file"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, size, webViewLink, webContentLink, owners'
            ).execute()
            return file
        except HttpError as e:
            logger.error(f"❌ Error getting file info for user {self.user.id}: {e}")
            return None


class GoogleAuthService:
    """Handle Google OAuth authentication - SCOPE FIX"""
    
    @staticmethod
    def validate_configuration():
        """Validate that all required settings are configured"""
        required_settings = [
            'GOOGLE_OAUTH_CLIENT_ID',
            'GOOGLE_OAUTH_CLIENT_SECRET',
        ]
        
        missing = []
        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing.append(setting)
        
        if missing:
            raise Exception(f"Missing required Google Drive settings: {', '.join(missing)}")
        
        return True
    
    @staticmethod
    def _get_redirect_uri():
        """Get the correct OAuth redirect URI"""
        # Try to get from settings first
        if hasattr(settings, 'BACKEND_URL'):
            redirect_uri = f"{settings.BACKEND_URL}/api/notes/google-callback/"
            logger.info(f"🔐 Using redirect URI from BACKEND_URL: {redirect_uri}")
            return redirect_uri
        
        # Fallback to environment-based
        if settings.DEBUG:
            redirect_uri = 'http://localhost:8000/api/notes/google-callback/'
        else:
            redirect_uri = 'https://sk-learntrack-pkw6.onrender.com/api/notes/google-callback/'
        
        logger.info(f"🔐 Using fallback redirect URI: {redirect_uri}")
        return redirect_uri
    
    @staticmethod
    def _get_client_config():
        """Get OAuth client configuration from settings"""
        GoogleAuthService.validate_configuration()
        
        redirect_uri = GoogleAuthService._get_redirect_uri()
        
        logger.info("=" * 60)
        logger.info("🔐 GOOGLE OAUTH CONFIGURATION")
        logger.info(f"   Client ID: {settings.GOOGLE_OAUTH_CLIENT_ID[:20]}...")
        logger.info(f"   Redirect URI: {redirect_uri}")
        logger.info(f"   Scopes: {', '.join(SCOPES)}")
        logger.info("=" * 60)
        
        return {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
    
    @staticmethod
    def get_oauth_url(request):
        """Generate Google OAuth URL - SCOPE FIX"""
        try:
            # Validate configuration first
            GoogleAuthService.validate_configuration()
            
            # Get client configuration
            client_config = GoogleAuthService._get_client_config()
            redirect_uri = GoogleAuthService._get_redirect_uri()
            
            # Generate secure state token
            random_token = secrets.token_urlsafe(32)
            state = f"{request.user.id}:{random_token}"
            
            # Store in session with extended expiry
            request.session['google_auth_state'] = state
            request.session['google_auth_user_id'] = request.user.id
            request.session.set_expiry(600)  # 10 minutes
            request.session.modified = True
            request.session.save()
            
            logger.info(f"🔐 Generated OAuth state for user {request.user.id}: {state[:20]}...")
            logger.info(f"🔐 Session keys: {list(request.session.keys())}")
            logger.info(f"🔐 Requesting scopes: {SCOPES}")
            
            # Create flow with ALL scopes
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,  # ✅ CRITICAL: Use all scopes
                redirect_uri=redirect_uri
            )
            
            # Generate authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type='offline',  # Get refresh token
                include_granted_scopes='true',
                state=state,
                prompt='consent'  # Force consent screen to get refresh token
            )
            
            logger.info(f"✅ Generated OAuth URL for user {request.user.id}")
            logger.info(f"🔗 Redirect URI: {redirect_uri}")
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"❌ Auth URL generation error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    def handle_callback(request):
        """Handle Google OAuth callback - SCOPE FIX"""
        try:
            # Get parameters
            code = request.GET.get('code')
            state = request.GET.get('state')
            error = request.GET.get('error')
            
            # Log everything for debugging
            logger.info("=" * 60)
            logger.info("🔐 OAUTH CALLBACK RECEIVED")
            logger.info(f"   Code: {code[:20] if code else 'None'}...")
            logger.info(f"   State: {state[:20] if state else 'None'}...")
            logger.info(f"   Error: {error}")
            logger.info(f"   Session keys: {list(request.session.keys())}")
            logger.info("=" * 60)
            
            # Check for OAuth errors
            if error:
                logger.error(f"❌ OAuth error: {error}")
                raise Exception(f"OAuth error: {error}")
            
            if not code or not state:
                raise Exception("Missing code or state parameter")
            
            # Validate state token
            session_state = request.session.get('google_auth_state')
            user_id = request.session.get('google_auth_user_id')
            
            logger.info(f"🔍 State validation:")
            logger.info(f"   Received: {state[:20]}...")
            logger.info(f"   Session: {session_state[:20] if session_state else 'None'}...")
            logger.info(f"   User ID: {user_id}")
            
            if not session_state or not user_id:
                # Try to extract from state as fallback
                if ':' in state:
                    try:
                        user_id = int(state.split(':')[0])
                        logger.info(f"✅ Extracted user_id from state: {user_id}")
                    except (ValueError, IndexError):
                        raise Exception("Invalid state parameter - could not extract user ID")
                else:
                    raise Exception("Session expired or invalid - no state found")
            elif state != session_state:
                raise Exception(f"State mismatch - CSRF protection triggered")
            
            # Get user
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"✅ Found user: {user.email} (ID: {user.id})")
            except User.DoesNotExist:
                raise Exception(f"User not found: {user_id}")
            
            # Get client configuration
            client_config = GoogleAuthService._get_client_config()
            redirect_uri = GoogleAuthService._get_redirect_uri()
            
            # Create flow with ALL scopes
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,  # ✅ CRITICAL: Use all scopes
                state=state,
                redirect_uri=redirect_uri
            )
            
            # Fetch token
            logger.info(f"🔄 Exchanging code for token with scopes: {SCOPES}...")
            flow.fetch_token(
                authorization_response=request.build_absolute_uri(),
                code=code
            )
            credentials = flow.credentials
            
            logger.info(f"✅ Token exchange successful")
            logger.info(f"   Access token: {credentials.token[:20]}...")
            logger.info(f"   Refresh token: {credentials.refresh_token[:20] if credentials.refresh_token else 'None'}...")
            logger.info(f"   Expires at: {credentials.expiry}")
            logger.info(f"   Scopes granted: {credentials.scopes}")
            
            # Save credentials
            drive_service = GoogleDriveService.__new__(GoogleDriveService)
            drive_service.user = user
            token_path = drive_service._get_token_path()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(token_path), exist_ok=True)
            
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)
            
            logger.info(f"✅ Credentials saved to: {token_path}")
            
            # Clear session
            request.session.pop('google_auth_state', None)
            request.session.pop('google_auth_user_id', None)
            
            logger.info(f"✅ Google Drive connected for user {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ OAuth callback error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    def disconnect(user):
        """Disconnect Google Drive for a user"""
        try:
            drive_service = GoogleDriveService.__new__(GoogleDriveService)
            drive_service.user = user
            token_path = drive_service._get_token_path()
            
            if os.path.exists(token_path):
                os.remove(token_path)
                logger.info(f"✅ Disconnected Google Drive for user {user.id}")
                return True
            else:
                logger.warning(f"⚠️ No token found for user {user.id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error disconnecting Google Drive for user {user.id}: {e}")
            return False


# Utility function
def is_google_drive_configured():
    """Check if Google Drive is properly configured in settings"""
    try:
        return all([
            hasattr(settings, 'GOOGLE_OAUTH_CLIENT_ID'),
            hasattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET'),
            settings.GOOGLE_OAUTH_CLIENT_ID,
            settings.GOOGLE_OAUTH_CLIENT_SECRET,
            settings.GOOGLE_OAUTH_CLIENT_ID != 'your-google-client-id.apps.googleusercontent.com'
        ])
    except:
        return False
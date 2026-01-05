# FILE: notes/google_drive_service.py - UNIFIED SERVICE
# ============================================================================

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
import os
import pickle
import logging
import secrets
from io import BytesIO
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']
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
                logger.info(f"Loaded credentials for user {self.user.id}")
            except Exception as e:
                logger.error(f"Error loading credentials: {e}")
                self.creds = None
        
        # Refresh or validate credentials
        if self.creds:
            if self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    # Save refreshed credentials
                    with open(token_path, 'wb') as token:
                        pickle.dump(self.creds, token)
                    logger.info(f"Refreshed credentials for user {self.user.id}")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    self.creds = None
        
        if not self.creds or not self.creds.valid:
            raise Exception("Google Drive authentication required. Please reconnect.")
        
        # Build service
        self.service = build('drive', 'v3', credentials=self.creds)
        logger.info(f"Drive service built for user {self.user.id}")
    
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
            logger.error(f"Error checking connection: {e}")
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
                logger.info(f"Found existing folder for user {self.user.id}")
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
            
            logger.info(f"Created folder '{FOLDER_NAME}' for user {self.user.id}")
            return folder['id']
            
        except HttpError as e:
            logger.error(f"Error managing folder: {e}")
            raise Exception(f"Failed to create folder: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
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
                    
                    logger.info(f"Updated file {existing_file_id} for user {self.user.id}")
                    
                    return {
                        'id': file['id'],
                        'webViewLink': file.get('webViewLink'),
                        'webContentLink': file.get('webContentLink'),
                        'success': True,
                        'updated': True
                    }
                except HttpError as e:
                    if e.resp.status == 404:
                        logger.warning(f"File {existing_file_id} not found, creating new")
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
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Set file permissions to accessible by link
            self.service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            logger.info(f"Created new file for user {self.user.id}")
            
            return {
                'id': file['id'],
                'webViewLink': file.get('webViewLink'),
                'webContentLink': file.get('webContentLink'),
                'success': True,
                'updated': False
            }
            
        except HttpError as e:
            error_msg = f"HTTP Error uploading to Drive: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Error uploading to Drive: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def delete_file(self, file_id):
        """Delete a file from Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file {file_id} for user {self.user.id}")
            return True
        except HttpError as e:
            logger.error(f"Error deleting file: {e}")
            return False


class GoogleAuthService:
    """Handle Google OAuth authentication"""
    
    @staticmethod
    def get_oauth_url(request):
        """Generate Google OAuth URL"""
        try:
            client_secret_path = os.path.join(
                settings.BASE_DIR.parent,
                'client_secret.json'
            )
            
            if not os.path.exists(client_secret_path):
                raise Exception("Google Drive not configured. Please add client_secret.json")
            
            # Generate secure state token WITH user_id embedded
            random_token = secrets.token_urlsafe(32)
            state = f"{request.user.id}:{random_token}"  # FIX: Use colon consistently
            
            # Store in session
            request.session['google_auth_state'] = state
            request.session['google_auth_user_id'] = request.user.id
            request.session.modified = True
            
            # Force session save
            request.session.save()
            
            logger.info(f"Generated state for user {request.user.id}: {state}")
            
            flow = Flow.from_client_secrets_file(
                client_secret_path,
                scopes=SCOPES,
                redirect_uri=request.build_absolute_uri('/api/notes/google-callback/')
            )
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Auth URL generation error: {e}")
            raise
    
    @staticmethod
    def handle_callback(request):
        """Handle Google OAuth callback"""
        try:
            # Validate state token
            state = request.GET.get('state')
            session_state = request.session.get('google_auth_state')
            user_id = request.session.get('google_auth_user_id')
            
            if not state or state != session_state or not user_id:
                raise Exception("Invalid session or state mismatch")
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise Exception("User not found")
            
            # Exchange code for credentials
            client_secret_path = os.path.join(
                settings.BASE_DIR.parent,
                'client_secret.json'
            )
            
            flow = Flow.from_client_secrets_file(
                client_secret_path,
                scopes=SCOPES,
                state=state,
                redirect_uri=request.build_absolute_uri('/api/notes/google-callback/')
            )
            
            flow.fetch_token(authorization_response=request.build_absolute_uri())
            credentials = flow.credentials
            
            # Save credentials
            token_dir = os.path.join(settings.MEDIA_ROOT, 'google_tokens')
            os.makedirs(token_dir, exist_ok=True)
            token_path = os.path.join(token_dir, f'token_{user.id}.pickle')
            
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)
            
            # Clear session
            request.session.pop('google_auth_state', None)
            request.session.pop('google_auth_user_id', None)
            
            logger.info(f"Google Drive connected for user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            raise
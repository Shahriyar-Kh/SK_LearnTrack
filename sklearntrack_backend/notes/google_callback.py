# FILE: notes/google_callback.py - PRODUCTION FIX VERSION
# ============================================================================

from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.contrib.auth import get_user_model
import os
import pickle
import logging
from google_auth_oauthlib.flow import Flow
import json

logger = logging.getLogger(__name__)

# ✅ CRITICAL FIX: Include ALL scopes that Google adds
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.file'
]


class GoogleOAuthCallbackView(View):
    """Handle Google OAuth callback (separate from DRF views)"""
    
    def get(self, request):
        try:
            # Get state and code from URL
            state = request.GET.get('state')
            code = request.GET.get('code')
            error = request.GET.get('error')
            
            logger.info(f"🔐 Google callback received")
            logger.info(f"   State: {state[:20] if state else 'None'}...")
            logger.info(f"   Code: {code[:20] if code else 'None'}...")
            logger.info(f"   Error: {error}")
            logger.info(f"   Session keys: {list(request.session.keys())}")
            
            # Check for OAuth errors
            if error:
                logger.error(f"❌ OAuth error: {error}")
                return self._error_response(f"OAuth error: {error}")
            
            if not state or not code:
                logger.error("❌ Missing authentication parameters")
                return self._error_response("Missing authentication parameters")
            
            # Try to get user_id from session first
            user_id = request.session.get('google_auth_user_id')
            
            if not user_id:
                # Try to extract from state (colon format: userid:token)
                try:
                    if ':' in state:
                        user_id = int(state.split(':')[0])
                        logger.info(f"✅ Extracted user_id from state: {user_id}")
                    elif '_' in state:
                        user_id = int(state.split('_')[0])
                        logger.info(f"✅ Extracted user_id from state: {user_id}")
                except (ValueError, IndexError):
                    logger.error(f"❌ Could not extract user_id from state: {state}")
                    return self._error_response("Invalid state parameter")
            
            if not user_id:
                logger.error("❌ No user_id found in session or state")
                return self._error_response("Session expired")
            
            # Get user
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"✅ Found user: {user.email} (ID: {user.id})")
            except User.DoesNotExist:
                logger.error(f"❌ User with id {user_id} not found")
                return self._error_response("User not found")
            
            # Get Google OAuth credentials from settings
            client_id = settings.GOOGLE_OAUTH_CLIENT_ID
            client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
            
            # ✅ CRITICAL: Log credentials info (not full values)
            logger.info(f"🔐 Checking Google OAuth configuration:")
            logger.info(f"   Client ID exists: {bool(client_id)}")
            logger.info(f"   Client Secret exists: {bool(client_secret)}")
            
            if client_id:
                logger.info(f"   Client ID first 10: {client_id[:10]}...")
                logger.info(f"   Client ID length: {len(client_id)}")
            
            if not client_id or not client_secret:
                logger.error("❌ Google OAuth credentials not configured in settings")
                return self._error_response("Server configuration error: Google OAuth not configured")
            
            # ✅ CRITICAL: Check if client_id ends with .apps.googleusercontent.com
            if not client_id.endswith('.apps.googleusercontent.com'):
                logger.error(f"❌ Invalid client_id format: {client_id}")
                return self._error_response(f"Invalid client ID format: {client_id}")
            
            # Create redirect URI
            redirect_uri = self._get_redirect_uri()
            logger.info(f"🔗 Using redirect URI: {redirect_uri}")
            
            try:
                # ✅ CRITICAL FIX: Use proper client configuration
                client_config = {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                }
                
                logger.info(f"🔐 Client config created")
                logger.info(f"   Auth URI: {client_config['web']['auth_uri']}")
                logger.info(f"   Token URI: {client_config['web']['token_uri']}")
                logger.info(f"   Redirect URI in config: {client_config['web']['redirect_uris'][0]}")
                logger.info(f"   Using scopes: {SCOPES}")
                
                # ✅ CRITICAL FIX: Use ALL scopes
                flow = Flow.from_client_config(
                    client_config,
                    scopes=SCOPES,  # Include ALL scopes
                    redirect_uri=redirect_uri
                )
                
                # Set the state to match what was passed
                flow.state = state
                
                # ✅ CRITICAL FIX: For Render production, ensure HTTPS
                if not settings.DEBUG:
                    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
                
                # Fetch token
                logger.info(f"🔄 Exchanging code for token...")
                flow.fetch_token(
                    authorization_response=request.build_absolute_uri(),
                    code=code
                )
                
                credentials = flow.credentials
                
                logger.info(f"✅ Successfully obtained credentials")
                logger.info(f"   Access token obtained: {bool(credentials.token)}")
                logger.info(f"   Refresh token obtained: {bool(credentials.refresh_token)}")
                logger.info(f"   Scopes granted: {credentials.scopes}")
                logger.info(f"   Expires at: {credentials.expiry}")
                
            except Exception as e:
                logger.error(f"❌ Error fetching token: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                
                # ✅ CRITICAL: Provide specific error guidance
                error_msg = str(e)
                if 'invalid_client' in error_msg.lower():
                    guidance = """
                    <div style="background: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <h4 style="margin-top: 0; color: #991b1b;">Possible Solutions:</h4>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Check that GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET are correctly set in your Render environment variables</li>
                            <li>Ensure the Client ID ends with ".apps.googleusercontent.com"</li>
                            <li>Verify the redirect URI in Google Cloud Console matches: <code>{redirect_uri}</code></li>
                            <li>Make sure the OAuth consent screen is configured with all required scopes</li>
                            <li>Check that your Google Cloud project has the Drive API enabled</li>
                        </ol>
                        <p style="margin: 10px 0; color: #991b1b;"><strong>Check your Render environment variables:</strong></p>
                        <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px;">
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
BACKEND_URL=https://sk-learntrack-pkw6.onrender.com
                        </pre>
                    </div>
                    """.format(redirect_uri=redirect_uri)
                    
                    return self._error_response(f"Invalid Client Configuration<br><br>{guidance}")
                else:
                    return self._error_response(f"Token exchange failed: {error_msg}")
            
            # Save credentials
            token_dir = os.path.join(settings.MEDIA_ROOT, 'google_tokens')
            os.makedirs(token_dir, exist_ok=True)
            token_path = os.path.join(token_dir, f'token_{user.id}.pickle')
            
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(credentials, token)
                
                logger.info(f"✅ Saved credentials to {token_path}")
                
                # Clear session data
                for key in ['google_auth_state', 'google_auth_user_id']:
                    if key in request.session:
                        del request.session[key]
                
                return self._success_response(user)
                
            except Exception as e:
                logger.error(f"❌ Error saving credentials: {str(e)}")
                return self._error_response(f"Failed to save credentials: {str(e)}")
                
        except Exception as e:
            logger.error(f"❌ OAuth callback error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._error_response(f"Authentication failed: {str(e)}")
    
    def _get_redirect_uri(self):
        """Get the correct redirect URI for production"""
        # Always use BACKEND_URL from settings
        if hasattr(settings, 'BACKEND_URL'):
            redirect_uri = f"{settings.BACKEND_URL}/api/notes/google-callback/"
            logger.info(f"🔐 Using BACKEND_URL from settings: {settings.BACKEND_URL}")
        else:
            # Fallback for Render
            redirect_uri = 'https://sk-learntrack-pkw6.onrender.com/api/notes/google-callback/'
            logger.warning(f"⚠️ BACKEND_URL not set, using fallback: {redirect_uri}")
        
        return redirect_uri
    
    def _error_response(self, error_message):
        """Generate error response HTML"""
        return HttpResponse(f"""
            <html>
            <head>
                <title>Token Exchange Failed</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 600px;
                        margin: 20px;
                    }}
                    .error-icon {{
                        font-size: 64px;
                        color: #ef4444;
                        margin-bottom: 20px;
                    }}
                    h1 {{ color: #1f2937; margin: 0 0 10px 0; }}
                    p {{ color: #6b7280; margin: 10px 0; }}
                    code {{ 
                        background: #f3f4f6; 
                        padding: 10px; 
                        border-radius: 4px;
                        font-size: 12px;
                        display: block;
                        margin: 10px 0;
                        word-wrap: break-word;
                        text-align: left;
                    }}
                    .guidance {{
                        background: #fee2e2;
                        border-left: 4px solid #dc2626;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error-icon">❌</div>
                    <h1>Token Exchange Failed</h1>
                    <p>There was an error connecting to Google Drive.</p>
                    <code>{error_message}</code>
                    <p style="margin-top: 20px;">Please try connecting again.</p>
                </div>
                <script>
                    // Send error message to opener
                    try {{
                        if (window.opener && !window.opener.closed) {{
                            window.opener.postMessage({{
                                type: 'google-auth-error',
                                error: 'Token exchange failed'
                            }}, '*');
                        }}
                    }} catch(e) {{
                        console.log('Could not send error to opener:', e);
                    }}
                    
                    setTimeout(function() {{
                        window.close();
                    }}, 5000);
                </script>
            </body>
            </html>
        """, status=400)
    
    def _success_response(self, user):
        """Generate success response HTML"""
        return HttpResponse(f"""
            <html>
            <head>
                <title>Google Drive Connected</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                        margin: 20px;
                    }}
                    .success-icon {{
                        font-size: 64px;
                        color: #10b981;
                        margin-bottom: 20px;
                    }}
                    h1 {{ color: #1f2937; margin: 0 0 10px 0; }}
                    p {{ color: #6b7280; margin: 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✓</div>
                    <h1>Google Drive Connected!</h1>
                    <p>Your account has been successfully linked with Google Drive.</p>
                    <p>You can now export notes directly to your Google Drive.</p>
                    <p style="margin-top: 20px; font-size: 14px;">This window will close automatically...</p>
                </div>
                <script>
                    // Send success message to opener
                    try {{
                        if (window.opener && !window.opener.closed) {{
                            window.opener.postMessage({{
                                type: 'google-auth-success',
                                message: 'Google Drive connected successfully!',
                                userId: {user.id}
                            }}, '*');
                            
                            // Also trigger a page reload to refresh auth status
                            setTimeout(function() {{
                                window.opener.location.reload();
                            }}, 1000);
                        }}
                    }} catch(e) {{
                        console.log('Could not send message to opener:', e);
                    }}
                    
                    // Auto-close after 2 seconds
                    setTimeout(function() {{
                        window.close();
                    }}, 2000);
                </script>
            </body>
            </html>
        """)
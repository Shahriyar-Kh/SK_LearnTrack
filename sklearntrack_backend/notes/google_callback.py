# FILE: notes/google_callback.py - SCOPE FIX VERSION
# ============================================================================
# CRITICAL FIX: Include all OAuth scopes that Google adds automatically
# ============================================================================

from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.contrib.auth import get_user_model
import os
import pickle
import logging
from google_auth_oauthlib.flow import Flow

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
            
            logger.info(f"🔐 Google callback received")
            logger.info(f"   State: {state[:20] if state else 'None'}...")
            logger.info(f"   Code: {code[:20] if code else 'None'}...")
            logger.info(f"   Session keys: {list(request.session.keys())}")
            
            if not state or not code:
                logger.error("❌ Missing authentication parameters")
                return HttpResponse("""
                    <html><body>
                        <h1>Error: Missing authentication parameters</h1>
                        <p>Please try connecting Google Drive again.</p>
                    </body></html>
                """, status=400)
            
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
                    return HttpResponse("""
                        <html><body>
                            <h1>Error: Invalid state parameter</h1>
                            <p>Please try connecting Google Drive again.</p>
                        </body></html>
                    """, status=400)
            
            if not user_id:
                logger.error("❌ No user_id found in session or state")
                return HttpResponse("""
                    <html><body>
                        <h1>Error: Session expired</h1>
                        <p>Please try connecting Google Drive again.</p>
                    </body></html>
                """, status=400)
            
            # Get user
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"✅ Found user: {user.email} (ID: {user.id})")
            except User.DoesNotExist:
                logger.error(f"❌ User with id {user_id} not found")
                return HttpResponse("<h1>User not found</h1>", status=404)
            
            # Get Google OAuth credentials from settings
            client_id = settings.GOOGLE_OAUTH_CLIENT_ID
            client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
            
            if not client_id or not client_secret:
                logger.error("❌ Google OAuth credentials not configured in settings")
                return HttpResponse(
                    "<h1>Server configuration error: Google OAuth not configured</h1>", 
                    status=500
                )
            
            # Create redirect URI
            if hasattr(settings, 'BACKEND_URL'):
                redirect_uri = f"{settings.BACKEND_URL}/api/notes/google-callback/"
            elif settings.DEBUG:
                redirect_uri = 'http://localhost:8000/api/notes/google-callback/'
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            else:
                redirect_uri = 'https://sk-learntrack-pkw6.onrender.com/api/notes/google-callback/'
            
            logger.info(f"🔗 Using redirect URI: {redirect_uri}")
            logger.info(f"🔐 Using scopes: {SCOPES}")
            
            try:
                # Create OAuth flow with environment variables
                client_config = {
                    "web": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                }
                
                # ✅ CRITICAL FIX: Use ALL scopes
                flow = Flow.from_client_config(
                    client_config,
                    scopes=SCOPES,  # Include ALL scopes
                    redirect_uri=redirect_uri
                )
                
                # Set the state to match what was passed
                flow.state = state
                
                # Fetch token
                logger.info(f"🔄 Exchanging code for token...")
                flow.fetch_token(
                    authorization_response=request.build_absolute_uri(),
                    code=code
                )
                
                credentials = flow.credentials
                
                logger.info(f"✅ Successfully obtained credentials")
                logger.info(f"   Access token: {credentials.token[:20]}...")
                logger.info(f"   Refresh token: {credentials.refresh_token[:20] if credentials.refresh_token else 'None'}...")
                logger.info(f"   Scopes: {credentials.scopes}")
                
            except Exception as e:
                logger.error(f"❌ Error fetching token: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
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
                                padding: 2px 6px; 
                                border-radius: 4px;
                                font-size: 12px;
                                display: block;
                                margin: 10px 0;
                                word-wrap: break-word;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="error-icon">❌</div>
                            <h1>Token Exchange Failed</h1>
                            <p>There was an error connecting to Google Drive.</p>
                            <code>{str(e)}</code>
                            <p style="margin-top: 20px;">Please try connecting again.</p>
                        </div>
                        <script>
                            setTimeout(function() {{
                                window.close();
                            }}, 5000);
                        </script>
                    </body>
                    </html>
                """, status=400)
            
            # Save credentials
            token_dir = os.path.join(settings.MEDIA_ROOT, 'google_tokens')
            os.makedirs(token_dir, exist_ok=True)
            token_path = os.path.join(token_dir, f'token_{user.id}.pickle')
            
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(credentials, token)
                
                logger.info(f"✅ Saved credentials to {token_path}")
                
                # Clear session data
                for key in ['google_auth_state', 'google_auth_user_id', 'user_id']:
                    if key in request.session:
                        del request.session[key]
                
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
                
            except Exception as e:
                logger.error(f"❌ Error saving credentials: {str(e)}")
                return HttpResponse(f"""
                    <html><body>
                        <h1>Failed to save credentials</h1>
                        <p>{str(e)}</p>
                    </body></html>
                """, status=500)
                
        except Exception as e:
            logger.error(f"❌ OAuth callback error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return HttpResponse(f"""
                <html>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {str(e)}</p>
                    <script>
                        try {{
                            if (window.opener && !window.opener.closed) {{
                                window.opener.postMessage({{
                                    type: 'google-auth-error',
                                    error: 'Authentication failed'
                                }}, '*')
                            }}
                        }} catch(e) {{
                            console.log('Could not send error to opener:', e);
                        }}
                        
                        setTimeout(function() {{
                            window.close();
                        }}, 3000);
                    </script>
                </body>
                </html>
            """, status=400)
# FILE: notes/views/google_callback.py - Fix with OAUTHLIB_INSECURE_TRANSPORT
# ============================================================================

from django.http import HttpResponse
from django.views import View
from django.conf import settings
from django.contrib.auth import get_user_model
import os
import pickle
import logging
from google_auth_oauthlib.flow import Flow

# ADD THIS: Allow HTTP for local development
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for localhost

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleOAuthCallbackView(View):
    """Handle Google OAuth callback (separate from DRF views)"""
    
    def get(self, request):
        try:
            # Get state and code from URL
            state = request.GET.get('state')
            code = request.GET.get('code')
            
            logger.info(f"Google callback received - State: {state}, Code: {code}")
            logger.info(f"Session keys: {list(request.session.keys())}")
            
            if not state or not code:
                return HttpResponse("""
                    <html><body><h1>Error: Missing authentication parameters</h1></body></html>
                """, status=400)
            
            # Try to get user_id from session first
            user_id = request.session.get('google_auth_user_id')
            
            if not user_id:
                # Try to extract from state (colon format: userid:token)
                try:
                    if ':' in state:
                        user_id = int(state.split(':')[0])
                        logger.info(f"Extracted user_id from state (colon format): {user_id}")
                    elif '_' in state:
                        user_id = int(state.split('_')[0])
                        logger.info(f"Extracted user_id from state (underscore format): {user_id}")
                except (ValueError, IndexError):
                    logger.error(f"Could not extract user_id from state: {state}")
                    return HttpResponse("""
                        <html><body><h1>Error: Invalid state parameter</h1></body></html>
                    """, status=400)
            
            if not user_id:
                logger.error("No user_id found in session or state")
                return HttpResponse("""
                    <html><body><h1>Error: Session expired. Please try again.</h1></body></html>
                """, status=400)
            
            # Get user
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"User with id {user_id} not found")
                return HttpResponse("<h1>User not found</h1>", status=404)
            
            # Exchange code for credentials
            client_secret_path = os.path.join(
                settings.BASE_DIR.parent,
                'client_secret.json'
            )
            
            if not os.path.exists(client_secret_path):
                logger.error(f"client_secret.json not found at {client_secret_path}")
                return HttpResponse("<h1>Server configuration error</h1>", status=500)
            
            # Create redirect URI
            redirect_uri = 'http://localhost:8000/api/notes/google-callback/'
            
            try:
                # Set the environment variable for insecure transport
                # This is safe for local development only
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
                
                flow = Flow.from_client_secrets_file(
                    client_secret_path,
                    scopes=SCOPES,
                    redirect_uri=redirect_uri
                )
                
                # Set the state to match what was passed
                flow.state = state
                
                # Fetch token
                flow.fetch_token(
                    authorization_response=request.build_absolute_uri(),
                    code=code  # Explicitly pass the code
                )
                
                credentials = flow.credentials
                
                logger.info(f"Successfully obtained credentials for user {user.id}")
                logger.info(f"Access token: {credentials.token[:20]}...")
                logger.info(f"Refresh token: {credentials.refresh_token[:20] if credentials.refresh_token else 'None'}...")
                
            except Exception as e:
                logger.error(f"Error fetching token: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return HttpResponse(f"""
                    <html><body><h1>Token exchange failed</h1><p>{str(e)}</p></body></html>
                """, status=400)
            
            # Save credentials
            token_dir = os.path.join(settings.MEDIA_ROOT, 'google_tokens')
            os.makedirs(token_dir, exist_ok=True)
            token_path = os.path.join(token_dir, f'token_{user.id}.pickle')
            
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(credentials, token)
                
                logger.info(f"Saved credentials to {token_path}")
                
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
                logger.error(f"Error saving credentials: {str(e)}")
                return HttpResponse(f"""
                    <html><body><h1>Failed to save credentials</h1><p>{str(e)}</p></body></html>
                """, status=500)
                
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
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
                    </script>
                </body>
                </html>
            """, status=400)